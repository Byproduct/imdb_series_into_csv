# This is a script to fetch TV series data from IMDB while Cinemagoer is out of order at the moment (September 2024).
# You input the name of TV series and this script fetches details into two .csv files:
# series.csv: episode code / rating / episode name / date / plot summary
# series_ratings: imdb ratings in one .csv line per season

# The .csv files work nicely with conditional formatting in excel

# Fetching code is based on help provided by oaokm at https://github.com/cinemagoer/cinemagoer/issues/517


import csv
from datetime import datetime
from requests_html import HTMLSession
from time import process_time
import imdb
import json
from tqdm import tqdm

print("\n\nFetching TV series info from IMDB into .csv")
tv_series_name = input('Enter name of series: ')


class IMDbFetcher:
    def __init__(self, search_box: str, num=0, first=True):
        self.imdb_client = imdb.Cinemagoer(accessSystem='http')
        self.search_box = search_box
        self.session = HTMLSession()
        with open("data.json") as f:
            config = json.load(f)
        self.xpath = config.get("Xpath").get('episodeDataFormIMDB')
        self.selector = config.get("Selector").get('episodeDataFormIMDB')

        if self.search_box.startswith('t'):
            self.search_box = self.search_box.lstrip('t')

        if not self.search_box.isdigit() and num != -1:
            results = self.imdb_client.search_movie(self.search_box)
            self.search_result = results[0 if first else num]
        elif num == -1:
            results = self.imdb_client.search_movie(self.search_box)
            print("\n\n[Search Result]")
            for index, movie in enumerate(results):
                print(f"[{index}] {movie.get('title')}")
            selected = int(input("\n> "))
            self.search_result = results[selected]
        else:
            self.search_result = self.imdb_client.get_movie(self.search_box)

        self.imdb_client.update(self.search_result)

    def get_TV_series_information(self, seasons=[]):
        kind = self.search_result.get('kind', None)
        num_of_seasons = self.search_result.get("number of seasons", None)
        movie_id = self.search_result.movieID
        season_page_url = self.imdb_client.urls['movie_main'] % f"{movie_id}"

        if seasons and kind in ('tv series', 'tv mini series'):
            if seasons != "*":
                seasons.sort()
            else:
                seasons = range(1, num_of_seasons + 1)

            all_episodes = []
            season_ratings = []

            for season in seasons:
                season_page = self.session.get(f"{season_page_url}episodes?season={season}")
                episode_count = season_page.html.xpath(self.xpath.get("countOfEpisode"))

                season_ratings_list = []

                if season_page.status_code == 200:
                    for index, episode in enumerate(tqdm(episode_count, desc=f"[Season: {season} of {num_of_seasons}]")):
                        try:
                            episode_url = episode.find(self.selector.get("title"), first=True).attrs.get("href")
                            episode_title = episode.find(self.selector.get('title'), first=True).text.split("∙")[-1].strip()
                            episode_plot = episode.find(self.selector.get("plot"), first=True).text
                            episode_rating = episode.find(self.selector.get("rate"), first=True).text
                            episode_id = episode_url.split('/')[2][2:]

                            release_date_text = episode.find(self.selector.get("dateOfPost"), first=True).text
                            try:
                                release_date = datetime.strptime(release_date_text, "%a, %b %d, %Y").strftime("%Y-%m-%d")
                            except ValueError:
                                release_date = release_date_text

                            all_episodes.append({
                                'episode_code': f"S{season}.E{index + 1}",
                                'rating': episode_rating,
                                'name': episode_title,
                                'release_date': release_date,
                                'plot': episode_plot
                            })

                            season_ratings_list.append(episode_rating)

                        except AttributeError:
                            continue
                
                season_ratings.append(season_ratings_list)

            # Episode details to {tv_series_name}.csv
            with open(f'{tv_series_name}.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['episode_code', 'rating', 'name', 'release_date', 'plot'])
                writer.writeheader()
                writer.writerows(all_episodes)

            # Episode ratings to {tv_series_name}_ratings.csv
            with open(f'{tv_series_name}_ratings.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for season_rating in season_ratings:
                    writer.writerow(season_rating)

        return []


print("Downloading data...")

try:
    movie = IMDbFetcher(
        search_box=f"{tv_series_name}",
        num=0
    )
    movie.get_TV_series_information(seasons='*')
    print(f"Episode details written to {tv_series_name}.csv")
    print(f"Episode ratings written to {tv_series_name}_ratings.csv")

except KeyboardInterrupt:
    print('Exit')
    exit()