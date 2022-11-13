"""Utility methods for parsing Google Takeout data."""
import zipfile
import json
import dataclasses as dc
from pathlib import Path
from typing import List, Dict, Iterator, Union, TextIO


@dc.dataclass
class ActivitySegment:
    """Represent an ActivitySegment record. Does not represent all fields."""
    start_lat_e7: int
    start_lon_e7: int
    end_lat_e7: int
    end_lon_e7: int
    start_timestamp: str
    end_timestamp: str
    distance: int
    activity_type: str
    confidence: str
    # Travel distance (meters) derived from waypoints
    travel_distance: float


@dc.dataclass
class PlaceVisit:
    """Represent a PlaceVisit record. Does not represent all fields."""
    lat_e7: int
    lon_e7: int
    # Note: address will usually contain commas. Keep in mind when writing to CSV.
    address: str
    name: str
    place_id: str
    start_timestamp: str
    end_timestamp: str
    confidence: str


@dc.dataclass
class TakeoutData:
    """Stores data extracted from a takeout."""
    activities: List[ActivitySegment] = dc.field(default_factory=list)
    places: List[PlaceVisit] = dc.field(default_factory=list)
    num_files = 0


def read_takeout(filepath: Path) -> TakeoutData:
    """
    Reads the takeout data at `filepath`, which may be zipped or unzipped.

    If the takeout data is zipped, this function will read the internal
    files without extracting them. If the takeout data has been extracted
    into a directory, then this function will simply read the files off
    the file system.

    Raises ValueError if the given takeout does not have the expected structure.
    """
    # Note: it just so happens that `Path` and `zipfile.Path` share the
    # same interface for the things that we want to do. Therefore, we
    # can use them interchangeably.
    if filepath.suffix == '.zip':
        if not zipfile.is_zipfile(filepath):
            raise ValueError(f'Invalid zipfile ({filepath})')
        data_paths = find_data_paths(zipfile.Path(zipfile.ZipFile(filepath)))
    elif filepath.is_dir():
        data_paths = find_data_paths(filepath)
    else:
        raise ValueError('Invalid file: neither a zip or a directory')

    takeout = TakeoutData()
    for file_path in data_paths:
        with file_path.open(mode='r', encoding='utf-8') as f:
            parse_history(f, takeout.activities, takeout.places)
        takeout.num_files += 1
    return takeout


def find_data_paths(
        takeout_root: Union[Path, zipfile.Path],
) -> Iterator[Union[Path, zipfile.Path]]:
    """
    Given the root path to the takeout data, return all found data files.

    This works for both regular paths and zipfile paths because the
    interfaces are the same for the things that we want to do.
    """
    history_path = takeout_root / 'Takeout' / 'Location History' / 'Semantic Location History'
    if not history_path.is_dir():
        raise ValueError('Couldn\'t find Semantic Location History')
    for year_path in history_path.iterdir():
        for json_path in year_path.iterdir():
            yield json_path


def parse_history(
        file: TextIO,
        activity_segments: List[ActivitySegment],
        place_visits: List[PlaceVisit],
):
    """
    Parse a Semantic Location History JSON file that is passed
    as an open file descriptor in text ('r') mode.

    Reads the file, parses the data, and writes to the provided
    lists in-place.
    """
    data = json.load(file)
    for record in data['timelineObjects']:
        if 'activitySegment' in record:
            activity_segments.append(parse_activity_segment(record))
        elif 'placeVisit' in record:
            place_visits.append(parse_place_visit(record))
        else:
            raise NotImplementedError()


def parse_activity_segment(data: Dict) -> ActivitySegment:
    """Parse an 'activitySegment' JSON record."""
    assert 'activitySegment' in data
    data = data['activitySegment']
    # Note: I use .get() here because some values may be missing,
    # and we just store them as None
    if 'waypointPath' in data:
        distance = data['waypointPath'].get('distanceMeters')
    elif 'transitPath' in data:
        distance = data['transitPath'].get('distanceMeters')
    elif 'simplifiedRawPath' in data:
        distance = data['simplifiedRawPath'].get('distanceMeters')
    else:
        distance = None

    return ActivitySegment(
        data.get('startLocation', {}).get('latitudeE7'),
        data.get('startLocation', {}).get('longitudeE7'),
        data.get('endLocation', {}).get('latitudeE7'),
        data.get('endLocation', {}).get('longitudeE7'),
        data.get('duration', {}).get('startTimestamp'),
        data.get('duration', {}).get('endTimestamp'),
        data.get('distance'),
        data.get('activityType'),
        data.get('confidence'),
        distance,
    )


def parse_place_visit(data: Dict) -> PlaceVisit:
    """Parse a 'placeVisit' JSON record."""
    assert 'placeVisit' in data
    data = data['placeVisit']
    return PlaceVisit(
        data.get('location', {}).get('latitudeE7'),
        data.get('location', {}).get('longitudeE7'),
        data.get('location', {}).get('address'),
        data.get('location', {}).get('name'),
        data.get('location', {}).get('placeId'),
        data.get('duration', {}).get('startTimestamp'),
        data.get('duration', {}).get('endTimestamp'),
        data.get('placeConfidence'),
    )
