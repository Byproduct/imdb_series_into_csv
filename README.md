# IMDB series into .csv

This is a script to fetch TV series data from IMDB into CSV files.

At the time of writing (December 2024) neither Cinemagoer nor Cinemagoerng can provide a list of episodes, so this script traverses through the series by following "next episode" codes.

You input the code or url of the first episode, and this script fetches details into two .csv files:

series.csv: episode code / rating / episode name / date / plot summary

ratings.csv: imdb ratings in one .csv line per season

The .csv files work nicely with conditional formatting in excel

![script_screenshot_1](https://github.com/Byproduct/imdb_series_into_csv.py/blob/main/startrek1.png)

![script_screenshot_2](https://github.com/Byproduct/imdb_series_into_csv.py/blob/main/startrek2.png)
