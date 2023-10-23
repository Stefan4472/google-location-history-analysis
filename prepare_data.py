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
"""
A program that reads a Google Location History takeout file and writes the data to CSV.
Run `python prepare_data.py help` for more information.
"""
import click
import pandas as pd
from pathlib import Path
from typing import Optional
from takeout_parser import read_takeout


@click.command()
@click.argument("takeout_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--activities_path", type=click.Path(file_okay=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--places_path", type=click.Path(file_okay=True, dir_okay=False, path_type=Path)
)
def prepare_data(
    takeout_path: Path,
    activities_path: Optional[Path] = None,
    places_path: Optional[Path] = None,
):
    """
    Reads Google Location History Takeout data and writes it out to two CSV files,
    one containing ActivitySegment data and the other containing PlaceVisit data.

    TAKEOUT_PATH: path to the zipped Google Takeout folder.
    ACTIVITIES_PATH: path to where the ActivitySegments CSV will be written (defaults to 'activities.csv').
    PLACES_PATH: path to where the PlaceVisits CSV will be written (defaults to 'places.csv').
    """
    takeout = read_takeout(takeout_path)
    click.echo(f"Found {takeout.num_files} data files")

    # Note: use "|" as a separator because addresses may contain a comma.
    # Pandas will escape the commas and work correctly, but other programs
    # may have difficulty with escaping.
    activities_path = activities_path if activities_path else Path("activities.csv")
    activities = pd.DataFrame(data=takeout.activities)
    activities.to_csv(
        activities_path, sep="|", header=True, index=False, encoding="utf-8"
    )
    click.echo(
        f"Wrote {activities.shape[0]} ActivitySegments to {activities_path.absolute()}"
    )

    places_path = places_path if places_path else Path("places.csv")
    places = pd.DataFrame(data=takeout.places)
    places.to_csv(places_path, sep="|", header=True, index=False, encoding="utf-8")
    click.echo(f"Wrote {places.shape[0]} PlaceVisits to {places_path.absolute()}")


if __name__ == "__main__":
    prepare_data()
