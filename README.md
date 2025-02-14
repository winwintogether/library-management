# Library Management System

A Django REST Framework application for managing a library system with user authentication and book management.

## Features

- User authentication with JWT
- Book management (CRUD operations)
- Book Loan
- Admin panel
- API documentation with Swagger
- Docker support
- Pagination and filtering

## Setup

1. Clone the repository
2. Create a virtual environment and activate it. I used poetry.
3. Install dependencies: `pip install -r requirements.txt` or `poetry install`
4. Set up environment variables (copy .env.example to .env)
5. Run migrations: `cd library_management python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run the server: `python manage.py runserver`

## Docker Setup

1. Build and run the containers:
   ```bash
   docker-compose up --build
   ```

2. Create superuser in Docker:
   ```bash
   docker-compose exec web cd library_management && python manage.py createsuperuser
   ```

## API Endpoints

- `/admin` - Admin panel
- `/api/users/` - User management
- `/api/books/` - Book management
- `/api/loans/` - Book Loans
- `/api/token/` - JWT token generation
- `/api/token/refresh/` - JWT token refresh
- `/swagger/` - API documentation

## Testing

Run tests with:
```bash
python manage.py test
```

## Security Measures

- JWT authentication
- CSRF protection enabled
- SQL injection prevention through ORM
- XSS protection through Django's template system
- Proper user authorization checks