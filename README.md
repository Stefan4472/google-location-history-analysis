# google-location-history-analysis

Python scripts and notebooks to analyze [Google Location History](https://support.google.com/accounts/answer/4388034?hl=en) data retrieved from [Google Takeout](https://takeout.google.com/settings/takeout). 

You can use [prepare_data.py](prepare_data.py) to read your zipped Takeout data and write it out to CSV files. Then you can use the [analyze_activities](analyze_activities.ipynb) and [analyze_places](analyze_places.ipynb) Jupyter notebooks to analyze your data interactively.

This project uses the [Pandas](https://pandas.pydata.org/), [Matplotlib](https://matplotlib.org/), and [bokeh](https://bokeh.org) python libraries and was tested with Python 3.11. **The minimum version of Python required is 3.10 due to [a bug in the Zipfile library](https://bugs.python.org/issue40564) that existed before 3.10.**

# Setup

Clone this repository:
```shell
git clone https://github.com/Stefan4472/google-location-history-analysis.git
```

Create a python virtual environment:
```shell
cd google-location-history-analysis
python -m venv env
# Windows
call env\Scripts\activate
```

Install the required packages:
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

Go to the link shown in the command line, e.g. `http://localhost:8888/?token=...` and try out the `analyze_activities.ipynb` and `analyze_places.ipynb` notebooks on your own data!
