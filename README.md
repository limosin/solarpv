## Photovoltaic Solar Power Plant Performance model

### Steps to run the scripts-
1. Copy weather data file, lets say `kota.csv` to the main folder.
2. Navigate to src folder. Run the weather_script.py file, passing weather file name as argument.<br>
      `python weather_script.py kota`
3. Once completed, you can remove the original copied weather data file.
4. Copy the solar data file to data/solar/ folder which will be created after the second step.
5. Run the match_time.py script from src folder.<br>
      `python match_time.py`
6. Make changes according to the plant configuration to `config.json` inside the data folder.
7. Now you can use the model.ipynb Ipython Notebook for viewing the analysis.
