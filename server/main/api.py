import requests
import os
import dotenv
import json


class Movie():
    poster_base_url = "https://image.tmdb.org/t/p/w500"

    def __init__(self, adult, title, overview, poster_path, release_date, vote_average, popularity, language, backdrop_path, id):
        self.id = id
        self.title = title
        self.popularity = popularity
        self.adult = adult
        self.overview = overview
        self.poster_path = self.poster_base_url+poster_path
        self.release_date = release_date
        self.vote_average = vote_average
        self.language = language
        self.backdrop_path = self.poster_base_url + backdrop_path
        self.genres = self.get_genres(id)

    def __str__(self):
        return f"{self.title}"

    def json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def get_genres(movie_id):
        dotenv.load_dotenv()

        url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {os.getenv('TMDB_API_READ_TOKEN')}"
        }
        response = requests.get(url, headers=headers)
        # print(response.text)
        data = json.loads(response.text)

        genres = []
        for genre in data["genres"]:
            genres.append(genre["name"])

        return genres


def get_movies():
    popular_movies = []
    dotenv.load_dotenv()
    url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('TMDB_API_READ_TOKEN')}"
    }
    response = requests.get(url, headers=headers)

    a = json.loads(response.text)
    for i, k in a.items():
        if i == "results":
            for l in k:
                mov = Movie(l["adult"], l["title"], l["overview"], l["poster_path"], l["release_date"],
                            l["vote_average"], l["popularity"], l["original_language"], l["backdrop_path"], l["id"])
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


def get_movie(movie_id):
    dotenv.load_dotenv()

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('TMDB_API_READ_TOKEN')}"
    }
    response = requests.get(url, headers=headers)
    # print(response.text)
    data = json.loads(response.text)

    genres = []
    for genre in data["genres"]:
        genres.append(genre["name"])
    mov = Movie(data["adult"], data["title"], data["overview"], data["poster_path"], data["release_date"],
                data["vote_average"], data["popularity"], data["original_language"], data["backdrop_path"], data["id"])
    return mov


#     # {
#   "adult": false,
#   "backdrop_path": "/9oYdz5gDoIl8h67e3ccv3OHtmm2.jpg",
#   "belongs_to_collection": null,
#   "budget": 17500000,
#   "genres": [
#     {
#       "id": 27,
#       "name": "Horror"
#     },
#     {
#       "id": 878,
#       "name": "Science Fiction"
#     },
#     {
#       "id": 53,
#       "name": "Thriller"
#     }
#   ],
#   "homepage": "https://www.the-match-factory.com/catalogue/films/the-substance.html",
#   "id": 933260,
#   "imdb_id": "tt17526714",
#   "origin_country": [
#     "GB"
#   ],
#   "original_language": "en",
#   "original_title": "The Substance",
#   "overview": "A fading celebrity decides to use a black market drug, a cell-replicating substance that temporarily creates a younger, better version of herself.",
#   "popularity": 2092.279,
#   "poster_path": "/lqoMzCcZYEFK729d6qzt349fB4o.jpg",
#   "production_companies": [
#     {
#       "id": 10163,
#       "logo_path": "/16KWBMmfPX0aJzDExDrPxSLj0Pg.png",
#       "name": "Working Title Films",
#       "origin_country": "GB"
#     },
#     {
#       "id": 233939,
#       "logo_path": null,
#       "name": "Blacksmith",
#       "origin_country": "FR"
#     }
#   ],
#   "production_countries": [
#     {
#       "iso_3166_1": "FR",
#       "name": "France"
#     },
#     {
#       "iso_3166_1": "GB",
#       "name": "United Kingdom"
#     }
#   ],
#   "release_date": "2024-09-07",
#   "revenue": 38578699,
#   "runtime": 141,
#   "spoken_languages": [
#     {
#       "english_name": "English",
#       "iso_639_1": "en",
#       "name": "English"
#     }
#   ],
#   "status": "Released",
#   "tagline": "If you follow the instructions, what could go wrong?",
#   "title": "The Substance",
#   "video": false,
#   "vote_average": 7.3,
#   "vote_count": 1046
# }
def main():
    mov_list = []
    for movie in get_movies():
        mov_list.append(movie)
        # mov = Movie(id=movie_id, adult=movie.adult, backdrop_path=movie.backdrop_path, language=movie.language,
        #             overview=movie.overview, popularity=movie.popularity, poster_path=movie.poster_path, release_date=movie.release_date, title=movie.title, vote_average=movie.vote_average)
        # mov.save()
        # mov_list.append(mov)
        print(movie)
    print(len(mov_list))


if __name__ == "__main__":
    main()
