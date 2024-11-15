# code for setting up default information
from .api import get_movies
from .models import Movie, Theatre, Show, Food, TheatreAdmin
import json


def setup(movies=None):
    mov_list = []
    for movie in get_movies():

        mov = Movie.objects.create(movie_id=movie.id, adult=movie.adult, backdrop_path=movie.backdrop_path, language=movie.language,
                                   overview=movie.overview, popularity=movie.popularity, poster_path=movie.poster_path, release_date=movie.release_date, title=movie.title, vote_average=movie.vote_average, genre=json.dumps(movie.genres))
        mov.save()
        mov_list.append(mov)
    print(mov_list)
    # add theatres
    demo_theatres = [
        {'name': 'Grand Cinema', 'location': 'Downtown'},
        {'name': 'Cineplex 21', 'location': 'Uptown'},
        {'name': 'Movie Palace', 'location': 'Suburbs'},
        {'name': 'Star Movies', 'location': 'West End'},
        {'name': 'Royal Cinema', 'location': 'East Side'},
        {'name': 'Mega Pictures', 'location': 'North Mall'},
        {'name': 'Silver Screen', 'location': 'South Plaza'},
        {'name': 'City Films', 'location': 'Central Park'},
        {'name': 'Dream Theatre', 'location': 'Beach Road'},
        {'name': 'Prime Movies', 'location': 'Lake View'},
        {'name': 'Galaxy Cinema', 'location': 'Metro Station'},
        {'name': 'Vista Movies', 'location': 'Hill Side'},
        {'name': 'Capitol Cinema', 'location': 'Main Street'}
    ]
    theatre_list = []
    for theatre in demo_theatres:
        th = Theatre.objects.create(**theatre)
        th.save()
        theatre_list.append(th)
    if movies:
        return mov_list
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
        {'movie': mov_list[0], 'theatre': theatre_list[3],
            'time': '2024-11-22 17:00:00', "price": 150},
        {'movie': mov_list[1], 'theatre': theatre_list[4],
            'time': '2024-11-22 19:30:00', "price": 280},
        {'movie': mov_list[2], 'theatre': theatre_list[5],
            'time': '2024-11-23 18:00:00', "price": 220},
        {'movie': mov_list[3], 'theatre': theatre_list[6],
            'time': '2024-11-23 20:30:00', "price": 190},
        {'movie': mov_list[4], 'theatre': theatre_list[7],
            'time': '2024-11-24 16:30:00', "price": 250},
        {'movie': mov_list[5], 'theatre': theatre_list[8],
            'time': '2024-11-24 19:00:00', "price": 230},
        {'movie': mov_list[6], 'theatre': theatre_list[9],
            'time': '2024-11-25 17:30:00', "price": 200},
        {'movie': mov_list[7], 'theatre': theatre_list[10],
            'time': '2024-11-25 20:00:00', "price": 270},
        {'movie': mov_list[8], 'theatre': theatre_list[11],
            'time': '2024-11-26 18:30:00', "price": 240}
    ]

    # for show in demo_shows:
    #     Show.objects.create(**show)

    # add food items
    demo_food_items = [
        {'food_id': 100001, 'name': 'Popcorn', 'price': 500, 'description': 'Fresh, buttery popcorn - the perfect movie snack',
            'image': 'https://images.unsplash.com/photo-1585647347483-22b66260dfff'},
        {'food_id': 100002, 'name': 'Soda', 'price': 300, 'description': 'Ice-cold refreshing soft drinks in various flavors',
            'image': 'https://images.unsplash.com/photo-1581636625402-29b2a704ef13'},
        {'food_id': 100003, 'name': 'Nachos', 'price': 400, 'description': 'Crispy tortilla chips served with melted cheese sauce',
            'image': 'https://images.unsplash.com/photo-1513456852971-30c0b8199d4d'},
        {'food_id': 100004, 'name': 'Ice Cream', 'price': 350, 'description': 'Creamy ice cream in various delicious flavors',
            'image': 'https://images.unsplash.com/photo-1497034825429-c343d7c6a68f'},
        {'food_id': 100005, 'name': 'Pizza Slice', 'price': 600, 'description': 'Hot and cheesy pizza slice with assorted toppings',
            'image': 'https://images.unsplash.com/photo-1513104890138-7c749659a591'},
        {'food_id': 100006, 'name': 'Chicken Wings', 'price': 700, 'description': 'Crispy chicken wings with your choice of sauce',
            'image': 'https://images.unsplash.com/photo-1608039755401-742074f0548d'},
        {'food_id': 100007, 'name': 'French Fries', 'price': 400, 'description': 'Golden crispy fries seasoned to perfection',
            'image': 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877'},
        {'food_id': 100008, 'name': 'Cheese Burger', 'price': 550, 'description': 'Classic burger with cheese and fresh vegetables',
            'image': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd'},
        {'food_id': 100009, 'name': 'Water Bottle', 'price': 50, 'description': 'Pure mineral water in a convenient bottle',
            'image': 'https://images.unsplash.com/photo-1560023907-5f335a7108c7'}
    ]

    for food_item in demo_food_items:
        Food.objects.create(**food_item)

    # t_admin = TheatreAdmin(username="admin", password=b"admin", )


if __name__ == '__main__':
    setup()
