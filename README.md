# google-location-history-analysis

Python scripts and notebooks to analyze and visualize location history data from Google Takeout. Uses Pandas, Matplotlib, and Jupyter Notebook. Tested with Python 3.11 on a Windows system. The project is structured as follows:
- `history_parser` contains code for parsing Google Takeout data
- `analyze_activities.ipynb` is a notebook for analyzing ActivitySegments
- `analyze_places.ipynb` is a notebook for analyzing PlaceVisits
- `prepare_data.py` is a script that parses Google Takeout data and generates one CSV file containing ActivitySegment data and one containing PlaceVisit data

You can check out [this guide on how to download your Google Takeout data](https://www.howtogeek.com/725241/how-to-download-your-google-maps-data/).

**The minimum version of Python required is 3.10 due to [a bug in the Zipfile library](https://bugs.python.org/issue40564) that existed before 3.10**

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

Check out the notebooks for `analyze_activities.ipynb` and `analyze_places.ipynb`. In your browser, go to the link shown in the command line, e.g. `http://localhost:8888/?token=...`. The notebooks are `analyze_activities.ipynb` and `analyze_places.ipynb`.

# Ideas for Extension

- Join location data with the [Google Maps API](https://developers.google.com/maps/documentation/places/web-service/place-id) (via Place IDs) or use the lat/lon coordinates with an API such as [PositionStack](https://positionstack.com/documentation). However, I'm not sure whether that would bring any interesting insights
- Create a map visualization (e.g. using [Geopandas](https://geopandas.org/) with a heatmap of countries visited 
- Create a map visualization and draw the actual ActivitySegments on it using their lat/lon coordinates