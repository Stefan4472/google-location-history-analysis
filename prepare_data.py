"""CLI script that reads a takeout and writes the data to CSV."""
import click
import pandas as pd
from pathlib import Path
from typing import Optional
from history_parser import parser


@click.command()
@click.argument('takeout_path', type=click.Path(exists=True, path_type=Path))
@click.option('--activities_path', type=click.Path(file_okay=True, dir_okay=False, path_type=Path))
@click.option('--places_path', type=click.Path(file_okay=True, dir_okay=False, path_type=Path))
def prepare_data(
        takeout_path: Path,
        activities_path: Optional[Path] = None,
        places_path: Optional[Path] = None,
):
    """
    Read Google Takeout data and write out two consolidated CSV files,
    one containing ActivitySegment data and the other containing PlaceVisit
    data. The CSV files allow the data to be more easily processed by
    external programs. The CSV files will be delimited with the "|" character.

    TAKEOUT_PATH: path to the Google Takeout folder (unzipped)
    ACTIVITIES_PATH: path to write out the ActivitySegments CSV (default 'activities.csv')
    PLACES_PATH: path to write out the PlaceVisits CSV (default 'places.csv')
    """
    takeout = parser.read_takeout(takeout_path)
    click.echo(f'Found {takeout.num_files} data files')

    # Note: use "|" as a separator because addresses may contain a comma.
    # Pandas will escape the commas and work correctly, but other programs
    # may have difficulty with escaping.
    activities_path = activities_path if activities_path else Path('activities.csv')
    activities = pd.DataFrame(data=takeout.activities)
    activities.to_csv(activities_path, sep='|', header=True, index=False, encoding='utf-8')
    click.echo(f'Wrote {activities.shape[0]} ActivitySegments to {activities_path.absolute()}')

    places_path = places_path if places_path else Path('places.csv')
    places = pd.DataFrame(data=takeout.places)
    places.to_csv(places_path, sep='|', header=True, index=False, encoding='utf-8')
    click.echo(f'Wrote {places.shape[0]} PlaceVisits to {places_path.absolute()}')


if __name__ == '__main__':
    prepare_data()
