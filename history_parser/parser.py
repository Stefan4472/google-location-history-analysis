"""Utility methods for parsing Google Takeout data."""
import json
import dataclasses as dc
from pathlib import Path
from typing import List, Dict


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


def parse_history(
        filepath: Path,
        activity_segments: List[ActivitySegment],
        place_visits: List[PlaceVisit],
):
    """
    Parse an individual Semantic Location History JSON file and
    write the parsed objects to the provided lists in-place.
    """
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    for record in data['timelineObjects']:
        if 'activitySegment' in record:
            activity_segments.append(parse_activity_segment(record))
        elif 'placeVisit' in record:
            place_visits.append(parse_place_visit(record))
        else:
            raise NotImplementedError()
