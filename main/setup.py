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
    print(mov_list)
    # add theatres
    demo_theatres = [
        {'name': 'Grand Cinema', 'location': 'Downtown', 'seats': 250},
        {'name': 'Cineplex 21', 'location': 'Uptown', 'seats': 300},
        {'name': 'Movie Palace', 'location': 'Suburbs', 'seats': 200},
        {'name': 'Star Movies', 'location': 'West End', 'seats': 280},
        {'name': 'Royal Cinema', 'location': 'East Side', 'seats': 320},
        {'name': 'Mega Pictures', 'location': 'North Mall', 'seats': 350},
        {'name': 'Silver Screen', 'location': 'South Plaza', 'seats': 220},
        {'name': 'City Films', 'location': 'Central Park', 'seats': 270},
        {'name': 'Dream Theatre', 'location': 'Beach Road', 'seats': 230},
        {'name': 'Prime Movies', 'location': 'Lake View', 'seats': 290},
        {'name': 'Galaxy Cinema', 'location': 'Metro Station', 'seats': 310},
        {'name': 'Vista Movies', 'location': 'Hill Side', 'seats': 240},
        {'name': 'Capitol Cinema', 'location': 'Main Street', 'seats': 260}
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
        {'movie': mov_list[9], 'theatre': theatre_list[3],
         'time': '2024-11-12 19:00:00', "price": 150},
        {'movie': mov_list[10], 'theatre': theatre_list[4],
            'time': '2024-11-13 17:30:00', "price": 250},
        {'movie': mov_list[11], 'theatre': theatre_list[5],
            'time': '2024-11-14 20:30:00', "price": 180},
        {'movie': mov_list[12], 'theatre': theatre_list[6],
            'time': '2024-11-15 18:30:00', "price": 200},
        {'movie': mov_list[13], 'theatre': theatre_list[7],
            'time': '2024-11-16 21:00:00', "price": 270},
        {'movie': mov_list[14], 'theatre': theatre_list[8],
            'time': '2024-11-17 16:00:00', "price": 220},
        {'movie': mov_list[15], 'theatre': theatre_list[9],
            'time': '2024-11-18 19:30:00', "price": 190},
        {'movie': mov_list[16], 'theatre': theatre_list[10],
            'time': '2024-11-19 20:00:00', "price": 230},
        {'movie': mov_list[17], 'theatre': theatre_list[11],
            'time': '2024-11-20 18:00:00', "price": 280},
        {'movie': mov_list[18], 'theatre': theatre_list[2],
            'time': '2024-11-21 21:30:00', "price": 260},
        {'movie': mov_list[19], 'theatre': theatre_list[1],
         'time': '2024-11-21 21:30:00', "price": 260},
    ]

    for show in demo_shows:
        Show.objects.create(**show)

    # add food items
    demo_food_items = [
        {'name': 'Popcorn', 'price': 500},
        {'name': 'Soda', 'price': 300},
        {'name': 'Nachos', 'price': 400},
        {'name': 'Ice Cream', 'price': 350},
        {'name': 'Pizza Slice', 'price': 600},
        {'name': 'Chicken Wings', 'price': 700},
        {'name': 'French Fries', 'price': 400},
        {'name': 'Cheese Burger', 'price': 550},
        {'name': 'Water Bottle', 'price': 50}
    ]

    for food_item in demo_food_items:
        Food.objects.create(**food_item)

    # t_admin = TheatreAdmin(username="admin", password=b"admin", )


if __name__ == '__main__':
    setup()
