# code for setting up default information
from .api import get_movies
from .models import Movie, Theatre, Show, Food, TheatreAdmin
import json


def setup():
    mov_list = []
    for movie in get_movies():

        mov = Movie.objects.create(movie_id=movie.id, adult=movie.adult, backdrop_path=movie.backdrop_path, language=movie.language,
                                   overview=movie.overview, popularity=movie.popularity, poster_path=movie.poster_path, release_date=movie.release_date, title=movie.title, vote_average=movie.vote_average, genre=json.dumps(movie.genres))
        mov.save()
        mov_list.append(mov)

    # add theatres
    demo_theatres = [
        {'name': 'Grand Cinema', 'location': 'Downtown', 'seats': 250},
        {'name': 'Cineplex 21', 'location': 'Uptown', 'seats': 300},
        {'name': 'Movie Palace', 'location': 'Suburbs', 'seats': 200},
    ]
    theatre_list = []
    for theatre in demo_theatres:
        th = Theatre.objects.create(**theatre)
        th.save()
        theatre_list.append(th)

    # add shows
    demo_shows = [
        {'movie': mov_list[0], 'theatre': theatre_list[0],
            'time': '2024-11-02 18:00:00', "price": 100},
        {'movie': mov_list[1], 'theatre': theatre_list[1],
            'time': '2024-11-04 20:00:00', "price": 300},
        {'movie': mov_list[2], 'theatre': theatre_list[2],
            'time': '2024-11-05 22:00:00', "price": 200},
        {'movie': mov_list[3], 'theatre': theatre_list[0],
            'time': '2024-11-06 18:00:00', "price": 100},
        {'movie': mov_list[4], 'theatre': theatre_list[1],
            'time': '2024-11-07 20:00:00', "price": 300},
        {'movie': mov_list[5], 'theatre': theatre_list[2],
            'time': '2024-11-08 22:00:00', "price": 200},
        {'movie': mov_list[6], 'theatre': theatre_list[0],
         'time': '2024-11-07 18:00:00', "price": 100},
        {'movie': mov_list[7], 'theatre': theatre_list[1],
            'time': '2024-11-09 20:00:00', "price": 300},
        {'movie': mov_list[8], 'theatre': theatre_list[2],
            'time': '2024-11-10 22:00:00', "price": 200},
    ]

    for show in demo_shows:
        Show.objects.create(**show)

    # add food items
    demo_food_items = [
        {'name': 'Popcorn', 'price': 500},
        {'name': 'Soda', 'price': 300},
        {'name': 'Nachos', 'price': 400},
    ]

    for food_item in demo_food_items:
        Food.objects.create(**food_item)

    t_admin = TheatreAdmin(username="admin", password=b"admin", )


if __name__ == '__main__':
    setup()
