# google-location-history-analysis

Python scripts and notebooks to analyze and visualize location history data from Google Takeout. Uses Pandas, Matplotlib, and Jupyter Notebook. Tested with Python 3.9 on a Windows system. 
- `history_parser` contains code for parsing Google Takeout data
- `analyze_activities.ipynb` is a notebook for analyzing ActivitySegments
- `analyze_places.ipynb` is a notebook for analyzing PlaceVisits
- `prepare_data.py` is a script that parses Google Takeout data and generates one CSV file containing ActivitySegment data and one containing PlaceVisit data

# Set up

Install the requirements:
```shell
python -m pip install -r requirements.txt
```

Prepare your Takeout data:
```shell
python prepare_data.py <INSERT_PATH_TO_TAKEOUT_ZIP>
```

Start Jupyter Notebook:
```shell
python -m jupyter notebook
```

In your browser, go to the link shown in the command line, e.g. `http://localhost:8888/?token=...`. The notebooks are `analyze_activities.ipynb` and `analyze_places.ipynb`.

# Ideas for Extension

- Join location data with the [Google Maps API](https://developers.google.com/maps/documentation/places/web-service/place-id) (via Place IDs) or use the lat/lon coordinates with an API such as [PositionStack](https://positionstack.com/documentation). However, I'm not sure whether that would bring any interesting insights
- Create a map visualization (e.g. using [Geopandas](https://geopandas.org/) with a heatmap of countries visited 
- Create a map visualization and draw the actual ActivitySegments on it using their lat/lon coordinates