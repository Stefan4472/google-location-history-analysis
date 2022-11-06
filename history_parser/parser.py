import json
import logging
import pandas as pd
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
    if 'waypointPath' in data:
        distance = data['waypointPath']['distanceMeters']
    elif 'transitPath' in data:
        distance = data['transitPath']['distanceMeters']
    elif 'simplifiedRawPath' in data:
        distance = data['simplifiedRawPath']['distanceMeters']
    else:
        raise NotImplementedError(f'Unrecognized path type in {json.dumps(data)}')

    return ActivitySegment(
        data['startLocation']['latitudeE7'],
        data['startLocation']['longitudeE7'],
        data['endLocation']['latitudeE7'],
        data['endLocation']['longitudeE7'],
        data['duration']['startTimestamp'],
        data['duration']['endTimestamp'],
        data['distance'],
        data['activityType'],
        data['confidence'],
        distance,
    )


def parse_place_visit(data: Dict) -> PlaceVisit:
    return PlaceVisit(
        data['location']['latitudeE7'],
        data['location']['longitudeE7'],
        data['location']['address'].replace(',', ''),
        data['location']['name'].replace(',', '') if 'name' in data['location'] else 'UNKNOWN',
        data['location']['placeId'],
        data['duration']['startTimestamp'],
        data['duration']['endTimestamp'],
        data['placeConfidence'],
    )


@dc.dataclass
class LocationHistory:
    activity_segments: List[ActivitySegment] = dc.field(default_factory=list)
    place_visits: List[PlaceVisit] = dc.field(default_factory=list)


def parse_history(filepath: Path) -> LocationHistory:
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    history = LocationHistory()
    for record in data['timelineObjects']:
        if 'activitySegment' in record:
            try:
                history.activity_segments.append(parse_activity_segment(record['activitySegment']))
            except NotImplementedError as e:
                logging.warning(f'Ignoring ActivitySegment with startTime={record["activitySegment"]["duration"]["startTimestamp"]}')
        elif 'placeVisit' in record:
            history.place_visits.append(parse_place_visit(record['placeVisit']))
        else:
            raise NotImplementedError()
    return history


if __name__ == '__main__':
    # TODO: a `prepare_data` cli script that takes the path to the takeout data, reads all of it, and creates two CSV files
    path = Path('Semantic Location History') / '2022' / '2022_SEPTEMBER.json'
    history = parse_history(path)
    activities = pd.DataFrame(data=history.activity_segments)
    places = pd.DataFrame(data=history.place_visits)
    activities.to_csv('activities.csv', header=True, index=False, encoding='utf-8')
    places.to_csv('places.csv', header=True, index=False, encoding='utf-8')
