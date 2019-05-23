## Photovoltaic Solar Power Plant Performance model

### Steps to run the scripts-
- Copy weather data file, lets say `kota.csv` to the main folder.
- Navigate to src folder. Run the weather_script.py file, passing weather file name as argument.\n
      `python weather_script.py kota`
- Copy the solar data file to data/solar/ folder which will be created after the second step.
- Run the match_time.py script from src folder.
      `python match_time.py`
- Make changes according to the plant configuration to `config.json` inside the data folder.
- Now you can use the model.ipynb Ipython Notebook for viewing the analysis.
