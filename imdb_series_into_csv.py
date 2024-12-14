import csv
import re
import os
import sys

# The version of cinemagoer on PyPI may not work - install the newest version directly from github, e.g. pip install git+https://github.com/cinemagoer/cinemagoerng.git
from cinemagoerng import web

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Creating .csv files of a TV series in IMDB.\n")
    print("Enter the IMDb code or url of the first episode (e.g. tt0106336 or https://www.imdb.com/title/tt0106336/whatever)\n")
    print("Note: This needs to be the url/code of the first episode, not the series main page!\n")
    user_input = input().strip()


    # Check if the user gave an IMDB code
    if re.match(r'^tt\d+$', user_input):
        first_episode_id = user_input
    else:
        # If not, attempt to extract the code from a URL
        pattern = r'/tt\d+/'
        match = re.search(pattern, user_input)
        if match:
            first_episode_id = match.group(0).strip('/')
       
            # Validate the extracted ID
            if not re.match(r'^tt\d+$', first_episode_id):
                print("Error: Invalid IMDb code format.")
                sys.exit(1)
        else:
            print("Error: invalid IMDB code.")
            sys.exit(1)


    print("\n\n")
    current_id = first_episode_id

    if os.path.exists("series.csv"):
        os.remove("series.csv")
    if os.path.exists("ratings.csv"):
        os.remove("ratings.csv")

    # series.csv with header: episode_code,rating,title,date,plot
    with open("series.csv", "w", newline="", encoding="utf-8") as series_file:
        series_writer = csv.writer(series_file)
        series_writer.writerow(["episode_code","rating","title","date","plot"])  # header

    # ratings.csv will have one line per season:
    # The first field is the season number, followed by all the ratings of that season's episodes
    with open("ratings.csv", "w", newline="", encoding="utf-8") as ratings_file:
        ratings_writer = csv.writer(ratings_file)

    current_season = None
    season_ratings = []  # Will store float values of the ratings of one season

    first_iteration = True
    while current_id:
        episode = web.get_title(current_id)

        try:
            season = episode.season if episode.season else "?"
        except:
            errormsg = """
            Error fetching data.
            Possible reasons:
            
            1. This script b0rked
            2. Imdb/cimenagoerng has changed something
            3. Invalid IMDB code
            4. Entered code of the series. Should enter the code of the first episode instead.
            """
            print(errormsg)
            sys.exit(1)

        episode_num = episode.episode if episode.episode else "?"
        episode_code = f"S{season}E{episode_num}"
        title = episode.title if episode.title else "?"
        date = episode.release_date.strftime("%Y-%m-%d") if episode.release_date else "?"
        rating_str = f"{episode.rating:.1f}" if episode.rating else "?"
        plot = "No plot available"
        if episode.plot:
            # Try 'en-US', fallback to first available language if needed
            if 'en-US' in episode.plot:
                plot = episode.plot['en-US']
            else:
                # If 'en-US' not available, pick the first value
                first_plot_key = next(iter(episode.plot))
                plot = episode.plot[first_plot_key]

        # Write this episode's information to series.csv immediately
        with open("series.csv", "a", newline="", encoding="utf-8") as series_file:
            series_writer = csv.writer(series_file)
            series_writer.writerow([episode_code, rating_str, title, date, plot])

        # Handle ratings accumulation per season
        # If moved to a new season, and old season data exists, flush it to ratings.csv
        if current_season is not None and season != current_season:
            _write_season_ratings(current_season, season_ratings)
            season_ratings = []  # Reset for new season

        current_season = season

        # Add rating to current season's list if it's numeric
        if rating_str != "?":
            try:
                rating_float = float(rating_str)
                season_ratings.append(rating_float)
            except ValueError:
                # If rating is not numeric, ignore
                pass

        current_id = getattr(episode, 'next_episode', None)       
        if first_iteration:
            previous_episode = getattr(episode, 'previous_episode', None)       
            if previous_episode:
                print("Previous episode information found - this is probably not the first episode.")
                print("If you're intentionally getting partial data, press enter to proceed.")
                print("Otherwise cancel (e.g. CTRL+C) and enter the url/code of the first episode in the series.")
                input()

        print(f"{episode_code}  -  {rating_str}  -  {title}  -  {date}  -  {plot}\n")
        first_iteration = False

    # After the loop ends, flush the last season's data
    if current_season is not None and season_ratings:
        _write_season_ratings(current_season, season_ratings)


def _write_season_ratings(season, ratings):
    """Append one line to ratings.csv with the season and its collected ratings."""
    with open("ratings.csv", "a", newline="", encoding="utf-8") as ratings_file:
        ratings_writer = csv.writer(ratings_file)
        # Build row: first the season number, then each rating
        row = [f"Season {season}"] + [str(r) for r in ratings]
        ratings_writer.writerow(row)

if __name__ == "__main__":
    main()
