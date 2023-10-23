# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utility methods for parsing Google Takeout data."""
import zipfile
import json
import dataclasses as dc
from pathlib import Path
from typing import List, Dict, Iterator


@dc.dataclass
class ActivitySegment:
    """Stores data parsed from a single ActivitySegment."""

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
    """Stores data parsed from a single PlaceVisit."""

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
    Reads and returns the zipped takeout data stored at `filepath`.
    Raises ValueError if the takeout data could not be parsed.
    """
    if not zipfile.is_zipfile(filepath):
        raise ValueError(f"Invalid file: {filepath}. Expected a zip file.")
    takeout = TakeoutData()
    for file_path in find_data_paths(zipfile.Path(zipfile.ZipFile(filepath))):
        parse_history_file(file_path, takeout.activities, takeout.places)
        takeout.num_files += 1
    return takeout


def find_data_paths(takeout_root: zipfile.Path) -> Iterator[zipfile.Path]:
    """
    Given the root path to the takeout data, return all found data files.
    """
    history_path = (
        takeout_root / "Takeout" / "Location History" / "Semantic Location History"
    )
    if not history_path.is_dir():
        raise ValueError("Couldn't find Semantic Location History")
    for year_path in history_path.iterdir():
        for json_path in year_path.iterdir():
            yield json_path


def parse_history_file(
    file: zipfile.Path,
    activity_segments: List[ActivitySegment],
    place_visits: List[PlaceVisit],
):
    """
    Parses a Semantic Location History JSON file and adds results to the
    provided lists.
    """
    with file.open(mode="r", encoding="utf-8") as f:
        data = json.load(f)
        for record in data["timelineObjects"]:
            if "activitySegment" in record:
                activity_segments.append(parse_activity_segment(record))
            elif "placeVisit" in record:
                place_visits.append(parse_place_visit(record))
            else:
                raise NotImplementedError(f"Don't know how to parse {record}")


def parse_activity_segment(data: Dict) -> ActivitySegment:
    """Parses an 'activitySegment' JSON record."""
    data = data["activitySegment"]
    # Note: I use .get() here because some values may be missing,
    # and we just store them as None
    if "waypointPath" in data:
        distance = data["waypointPath"].get("distanceMeters")
    elif "transitPath" in data:
        distance = data["transitPath"].get("distanceMeters")
    elif "simplifiedRawPath" in data:
        distance = data["simplifiedRawPath"].get("distanceMeters")
    else:
        distance = None

    return ActivitySegment(
        data.get("startLocation", {}).get("latitudeE7"),
        data.get("startLocation", {}).get("longitudeE7"),
        data.get("endLocation", {}).get("latitudeE7"),
        data.get("endLocation", {}).get("longitudeE7"),
        data.get("duration", {}).get("startTimestamp"),
        data.get("duration", {}).get("endTimestamp"),
        data.get("distance"),
        data.get("activityType"),
        data.get("confidence"),
        distance,
    )


def parse_place_visit(data: Dict) -> PlaceVisit:
    """Parses a 'placeVisit' JSON record."""
    data = data["placeVisit"]
    return PlaceVisit(
        data.get("location", {}).get("latitudeE7"),
        data.get("location", {}).get("longitudeE7"),
        data.get("location", {}).get("address"),
        data.get("location", {}).get("name"),
        data.get("location", {}).get("placeId"),
        data.get("duration", {}).get("startTimestamp"),
        data.get("duration", {}).get("endTimestamp"),
        data.get("placeConfidence"),
    )
