import click
import sys
import pandas as pd
from pathlib import Path
from typing import Optional, List
from history_parser import parser
from history_parser.parser import ActivitySegment, PlaceVisit


@click.command()
@click.argument('takeout_path', type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option('--activities_path', type=click.Path(file_okay=True, dir_okay=False, path_type=Path))
@click.option('--places_path', type=click.Path(file_okay=True, dir_okay=False, path_type=Path))
def prepare_data(
        takeout_path: Path,
        activities_path: Optional[Path] = None,
        places_path: Optional[Path] = None,
):
    """
    Read Google Takeout data and write out two CSV files.

    TAKEOUT_PATH: path to the Google Takeout folder (unzipped)
    """
    # TODO: support unzipping the takeout file
    click.echo('Looking for "Semantic Location History" folder...')
    data_path = takeout_path / 'Takeout' / 'Location History' / 'Semantic Location History'
    if not data_path.is_dir():
        click.echo(f'The path {data_path.absolute()} is not a directory', err=True)
        sys.exit(1)

    num_files = 0
    parsed_activities: List[ActivitySegment] = []
    parsed_places: List[PlaceVisit] = []

    # Find YEAR files, e.g. '2020', '2021', '2022'
    for year_dir in data_path.iterdir():
        # Each year file contains the monthly data files
        for file_path in year_dir.iterdir():
            click.echo(f'Processing file {file_path}')
            parser.parse_history(file_path, parsed_activities, parsed_places)
            num_files += 1
    click.echo(f'Parsed a total of {num_files} files')

    # Note: use "|" as a separator because addresses may contain a comma.
    # Pandas will escape the commas and work correctly, but other programs
    # may have difficulty with escaping.
    activities_path = activities_path if activities_path else Path('activities.csv')
    activities = pd.DataFrame(data=parsed_activities)
    activities.to_csv(activities_path, sep='|', header=True, index=False, encoding='utf-8')
    click.echo(f'Wrote {activities.shape[0]} ActivitySegments to {activities_path.absolute()}')

    places_path = places_path if places_path else Path('places.csv')
    places = pd.DataFrame(data=parsed_places)
    places.to_csv(places_path, sep='|', header=True, index=False, encoding='utf-8')
    click.echo(f'Wrote {places.shape[0]} PlaceVisits to {places_path.absolute()}')


if __name__ == '__main__':
    prepare_data()
