# Fitness Class Booking API

A Django REST Framework backend for booking fitness classes. Users register and log in to receive JWT tokens, browse upcoming classes, book a seat in a class, and list their own bookings. Any authenticated user can create a new class, and both classes and bookings can be managed through the Django admin site.

## Highlights

- User registration with email format and password strength checks
- JWT login using Simple JWT (access and refresh tokens)
- Authenticated endpoint that returns the current user's profile
- Public listing of upcoming fitness classes, ordered by start time
- Class creation for authenticated users, with a check against duplicate instructor/time combinations
- Class booking that rejects duplicate bookings and fully booked classes, and decrements the available slots
- Per-user booking history
- Django admin registration for fitness classes and bookings

## Technology

| Area | Technology |
| --- | --- |
| Framework | Django 5.2.4, Django REST Framework 3.16.0 |
| Authentication | JWT with `djangorestframework_simplejwt` 5.5.0 (PyJWT 2.9.0) |
| Database | SQLite (`db.sqlite3`) |
| User model | Django built-in `django.contrib.auth.models.User` |
| Python | Python 3.10+ (Django 5.2 requirement); the project virtualenv was created with Python 3.13 |

## Request Flow

```text
Client
  |
  |  POST /api/user/register/        -> create account
  |  POST /api/user/login/           -> receive access + refresh tokens
  |
  |  Authorization: Bearer <access>
  v
Django REST Framework (JWTAuthentication)
  |
  +-- GET  /api/fittnessClass/get/     -> upcoming classes (public)
  +-- POST /api/fittnessClass/create/  -> create a class
  +-- POST /api/booking/book/          -> book a class, slots - 1
  +-- GET  /api/bookings/get/          -> current user's bookings
  |
  v
SQLite (auth_user, app_fitnessclass, app_booking)
```

## Project Structure

```text
booking_system/
├── app/
│   ├── migrations/      Initial migration for FitnessClass and Booking
│   ├── admin.py         Admin registration for FitnessClass and Booking
│   ├── models.py        FitnessClass and Booking models
│   ├── serializers.py   User, FitnessClass, and Booking serializers
│   ├── url.py           API routes
│   ├── validators.py    Email and password validation helpers
│   └── views.py         Function-based API views
├── booking/
│   ├── settings.py      Django, DRF, and Simple JWT settings
│   ├── urls.py          Root URLconf (admin + app routes)
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
└── requirements.txt
```

## Data Model

### FitnessClass

| Field | Type | Notes |
| --- | --- | --- |
| `id` | BigAutoField | Primary key |
| `name` | CharField(100) | Optional |
| `datetime` | DateTimeField | Required; class start time |
| `instructor` | CharField(100) | Optional at model level, required by the create endpoint |
| `available_slots` | PositiveIntegerField | Required; decremented on each booking |

### Booking

| Field | Type | Notes |
| --- | --- | --- |
| `id` | BigAutoField | Primary key |
| `fitness_class` | ForeignKey to `FitnessClass` | Cascade delete |
| `user` | ForeignKey to `User` | Cascade delete |
| `booked_at` | DateTimeField | Set automatically on creation |

## Getting Started

### Requirements

- Python 3.10 or newer
- pip

### Installation (Windows PowerShell)

```powershell
git clone <your-repository-url>
cd booking_system

python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On macOS or Linux, activate the environment with `source env/bin/activate`.

### Database Setup

```powershell
python manage.py migrate
python manage.py createsuperuser
```

### Run the Development Server

```powershell
python manage.py runserver
```

The API is served at `http://127.0.0.1:8000/` and the admin site at `http://127.0.0.1:8000/admin/`.

## Configuration

The project does not read environment variables or a `.env` file. All configuration lives in `booking/settings.py`:

| Setting | Current value |
| --- | --- |
| `SECRET_KEY` | Hard-coded development key |
| `DEBUG` | `True` |
| `ALLOWED_HOSTS` | `[]` (localhost only while `DEBUG=True`) |
| `DATABASES` | SQLite at `db.sqlite3` |
| `TIME_ZONE` / `USE_TZ` | `UTC` / `True` |
| `DEFAULT_AUTHENTICATION_CLASSES` | `rest_framework_simplejwt.authentication.JWTAuthentication` |
| `ACCESS_TOKEN_LIFETIME` | 60 minutes |
| `REFRESH_TOKEN_LIFETIME` | 1 day |
| `AUTH_HEADER_TYPES` | `Bearer` |

Replace the secret key, disable `DEBUG`, and set `ALLOWED_HOSTS` before running the project anywhere other than a local machine.

## Authentication

Protected endpoints require a JWT access token obtained from the login endpoint:

```http
Authorization: Bearer <access_token>
```

Access tokens expire after 60 minutes. A refresh token is returned at login, but the project does not expose a token refresh endpoint, so clients must log in again once the access token expires.

## API Endpoints

All routes are defined in `app/url.py`. Paths are listed exactly as implemented, including the `fittnessClass` spelling.

Every response body includes a `status` field containing a string (for example `"200"` or `"400"`), alongside either `message` or `data`.

### Users

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/api/user/register/` | None | Register a new user |
| POST | `/api/user/login/` | None | Log in and receive JWT tokens |
| GET | `/api/user/get/` | JWT | Get the current user's profile |

### Fitness Classes

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/api/fittnessClass/create/` | JWT | Create a new fitness class |
| GET | `/api/fittnessClass/get/` | None | List upcoming classes |

### Bookings

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/api/booking/book/` | JWT | Book a seat in a class |
| GET | `/api/bookings/get/` | JWT | List the current user's bookings |

### Admin

| Endpoint | Description |
| --- | --- |
| `/admin/` | Django admin for users, fitness classes, and bookings |

## Request and Response Examples

### Register

```bash
curl -X POST http://127.0.0.1:8000/api/user/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "jane", "email": "jane@example.com", "password": "Str0ng!Pass"}'
```

```json
{ "status": "200", "message": "User is successfully create ...!" }
```

Validation:

- `email` must match `^[\w\.-]+@[\w\.-]+\.\w+$`; otherwise `400` with `"Invalid email format"`.
- `password` must be at least 8 characters and contain an uppercase letter, a lowercase letter, a digit, and one of `!@#$%^&*(),.?":{}|<>`; otherwise `400` with `"Password is not strong enough."`.
- If a user with the same username and email already exists, the response is `400` with `"This username is already taken. Please choose another one."`.
- Any other serializer validation failure (for example, an existing username with a different email) returns `400` with `"Bad Request"`.

Django's `AUTH_PASSWORD_VALIDATORS` are not applied by this endpoint; only the custom rules above are enforced.

### Login

```bash
curl -X POST http://127.0.0.1:8000/api/user/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "jane", "password": "Str0ng!Pass"}'
```

```json
{
  "status": "200",
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

Invalid credentials return `400` with `"Invalid username or password"`.

### Current User

```bash
curl http://127.0.0.1:8000/api/user/get/ \
  -H "Authorization: Bearer <access_token>"
```

```json
{
  "status": "200",
  "data": { "id": 1, "username": "jane", "email": "jane@example.com" }
}
```

### Create a Fitness Class

```bash
curl -X POST http://127.0.0.1:8000/api/fittnessClass/create/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Morning Yoga", "datetime": "2026-11-01T07:00:00Z", "instructor": "Alex", "available_slots": 20}'
```

Response (HTTP `201 Created`):

```json
{
  "status": "200",
  "message": "Class created successfully",
  "data": {
    "id": 1,
    "name": "Morning Yoga",
    "datetime": "2026-11-01T07:00:00Z",
    "instructor": "Alex",
    "available_slots": 20
  }
}
```

Validation:

- `datetime`, `instructor`, and `available_slots` are required; `name` is optional. Missing fields return `400` with `"All fields (datetime, instructor, available_slots) are required."`. Because the check is a truthiness test, `available_slots: 0` is also rejected.
- A class with the same `datetime` and `instructor` cannot be created twice (returns `400`).
- `available_slots` must be a non-negative integer; serializer errors are returned in `message`.

### List Upcoming Classes

```bash
curl http://127.0.0.1:8000/api/fittnessClass/get/
```

Returns classes whose `datetime` is now or later, ordered by `datetime`:

```json
{
  "status": "200",
  "data": [
    {
      "id": 1,
      "name": "Morning Yoga",
      "datetime": "2026-11-01T07:00:00Z",
      "instructor": "Alex",
      "available_slots": 20
    }
  ]
}
```

### Book a Class

```bash
curl -X POST http://127.0.0.1:8000/api/booking/book/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"class_id": 1}'
```

```json
{ "status": "200", "message": "Booking successful" }
```

On success the class's `available_slots` is reduced by one.

| Condition | HTTP status | Message |
| --- | --- | --- |
| `class_id` missing | 400 | `class_id is required` |
| Class does not exist | 404 | `Class not found` |
| User already booked this class | 400 | `You have already booked this class` |
| `available_slots` is 0 | 404 | `No available slots` |

### List My Bookings

```bash
curl http://127.0.0.1:8000/api/bookings/get/ \
  -H "Authorization: Bearer <access_token>"
```

```json
{
  "status": "200",
  "data": [
    { "id": 1, "fitness_class": 1, "user": 1, "booked_at": "2026-10-03T09:15:42.123456Z" }
  ]
}
```

`fitness_class` and `user` are returned as primary keys.

## Admin Site

Log in at `/admin/` with the superuser created during setup. `FitnessClass` is listed with `id`, `name`, `instructor`, `available_slots`, and `datetime`; `Booking` is listed with `id`, `user`, `fitness_class`, and `booked_at`.

## Testing

`app/tests.py` contains no tests yet. The Django test runner can still be used once tests are added:

```powershell
python manage.py test
```
