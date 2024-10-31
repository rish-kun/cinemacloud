# code for setting up default information
from .api import get_movies
from .models import Movie, Theatre, Show, Food


def setup():
    mov_list = []
    # add movies
    for movie in get_movies():
        mov = Movie.objects.create(movie_id=movie.id, adult=movie.adult, backdrop_path=movie.backdrop_path, language=movie.language,
                                   overview=movie.overview, popularity=movie.popularity, poster_path=movie.poster_path, release_date=movie.release_date, title=movie.title, vote_average=movie.vote_average)
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
        {'movie_id': mov_list[0], 'theatre': theatre_list[0],
            'show_time': '2023-10-01 18:00:00'},
        {'movie_id': mov_list[1], 'theatre_id': theatre_list[1],
            'show_time': '2023-10-01 20:00:00'},
        {'movie_id': mov_list[2], 'theatre_id': theatre_list[2],
            'show_time': '2023-10-01 22:00:00'},
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
