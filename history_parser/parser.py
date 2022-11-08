import json
import logging
import dataclasses as dc
from pathlib import Path
from typing import List, Dict


@dc.dataclass
class ActivitySegment:
    start_lat_e7: int
    start_lon_e7: int
    end_lat_e7: int
    end_lon_e7: int
    start_timestamp: str
    end_timestamp: str
    distance: int
    activity_type: str
    confidence: str
    # TODO: waypoint data vs activity data?
    travel_distance_meters: float


@dc.dataclass
class PlaceVisit:
    lat_e7: int
    lon_e7: int
    # TODO: this may cause problems in CSV format, because addresses have commas
    address: str
    name: str
    place_id: str
    start_timestamp: str
    end_timestamp: str
    confidence: str


def parse_activity_segment(data: Dict) -> ActivitySegment:
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
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    for record in data['timelineObjects']:
        if 'activitySegment' in record:
            activity_segments.append(parse_activity_segment(record['activitySegment']))
        elif 'placeVisit' in record:
            place_visits.append(parse_place_visit(record['placeVisit']))
        else:
            raise NotImplementedError()


@dc.dataclass
class LocationHistory:
    activity_segments: List[ActivitySegment] = dc.field(default_factory=list)
    place_visits: List[PlaceVisit] = dc.field(default_factory=list)


def parse_history_util(filepath: Path) -> LocationHistory:
    history = LocationHistory()
    parse_history(filepath, history.activity_segments, history.place_visits)
    return history
