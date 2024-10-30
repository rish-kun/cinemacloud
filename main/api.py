import requests
import os
import dotenv
import json


class Movie():
    poster_base_url = "https://image.tmdb.org/t/p/w500"

    def __init__(self, adult, title, overview, poster_path, release_date, vote_average, popularity, language, backdrop_path):
        self.title = title
        self.popularity = popularity
        self.adult = adult
        self.overview = overview
        self.poster_path = self.poster_base_url+poster_path
        self.release_date = release_date
        self.vote_average = vote_average
        self.language = language
        self.backdrop_path = self.poster_base_url + backdrop_path

    def __str__(self):
        return f"{self.title}"


def get_movies():
    popular_movies = []
    dotenv.load_dotenv()
    url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv("TMDB_API_READ_TOKEN")}"
    }
    response = requests.get(url, headers=headers)

    a = json.loads(response.text)
    for i, k in a.items():
        if i == "results":
            for l in k:
                mov = Movie(l["adult"], l["title"], l["overview"], l["poster_path"], l["release_date"],
                            l["vote_average"], l["popularity"], l["original_language"], l["backdrop_path"])
                popular_movies.append(mov)
    # print(*popular_movies, sep="\n")
    return popular_movies


# props of a movie
# adult
# backdrop_path
# genre_ids
# id
# original_language
# original_title
# overview
# popularity
# poster_path - image which needs to be displayed
# release_date
# title
# video
# vote_average
# vote_count

# /wTnV3PCVW5O92JMrFvvrRcV39RU.jpg
