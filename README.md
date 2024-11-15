# CinemaCloud

A Django-based movie ticket booking system with features for users and theatre administrators. The application uses PostgreSQL for data storage and is containerized using Docker.

## Features

- User Authentication

  - Email & Password login
  - Google OAuth integration
  - Email verification system
  - Password reset functionality

- Booking System

  - Movie ticket booking
  - Food & beverage ordering
  - Ticket cancellation
  - Seat selection
  - Digital wallet for transactions

- Theatre Administration

  - Screen management
  - Show scheduling
  - Food item management
  - Revenue tracking
  - Transaction history

- Additional Features
  - Search functionality
  - Email notifications
  - Location-based theatre filtering
  - Secure payment processing

## Tech Stack

- Backend: Django
- Database: PostgreSQL
- Web Server: Nginx
- WSGI Server: Gunicorn
- Containerization: Docker
- Authentication: Django AllAuth

## Setup Instructions

### Development Environment

1. Clone the repository

2. Build and run the development containers:

```sh
docker-compose up --build
```

```sh
docker-compose -f docker-compose.prod.yml up --build
```

This will start:

- Django with Gunicorn
- PostgreSQL database
- Nginx server on port 8080

### Initial Setup

After the containers are running, set up the initial data:

1. Create database migrations:

```sh
docker-compose exec web python manage.py migrate
```

2. Load initial data (movies, theatres, etc.):

```sh
docker-compose exec web python manage.py setup
```

## Project Structure

```
├── nginx/                 # Nginx configuration
├── server/               # Django application
│   ├── main/            # Main application module
│   ├── oauth/           # OAuth integration
│   ├── th_admin/        # Theatre admin module
│   └── templates/       # HTML templates
├── docker-compose.yml    # Development configuration
└── docker-compose.prod.yml # Production configuration
```

## Contributing

Please ensure all new features include appropriate tests and documentation.

## License

All rights reserved. Unauthorized copying or distribution is prohibited.

```

```
