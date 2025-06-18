
# Fitness Class Booking API

A Django RESTful API that allows users to register, login, view upcoming fitness classes, book them, and view their bookings. Admins/instructors can also create new fitness classes.

##  Features
- User register &  JWT Authentication
- Secure Login with Token-based Auth
- view all Upcoming Fitness Classes 
- Create New Classes (Authenticated)
- Book Fitness Classes (Avoid Overbooking)
- view Your Bookings
- Duplicate booking & slot validations

## Tech stack
- Python 3.x
- Django 4.x
- Django REST Framework
- SQLite (default, can be changed)
- Simple JWT Authentication

## API Endpoints

### Authentication

|method | Endpoint        | Description                   |
|-------|-----------------|-------------------------------|
| POST  | user/register/  | Register new user             |
| POST  | user/login/     | Login JWT tokens              | 
| GET   | user/get/       | Get current user jwt required | 
 

### Fitness Classes

|method | Endpoint              | Description                     |
|-------|-----------------------|---------------------------------|
| POST  | fittnessClass/create/ | create new class auth required  | 
| GET   | fittnessClass/get/    | List all upcoming classes       |


### Bookings

|method | Endpoint       | Description                         |
|-------|----------------|-------------------------------------|
| POST  | booking/book/  | Book a class JWT required           |
| GET   | bookings/get/  | Get all bookings for logged-in user | 


## Validations & Error Handling

- Email format and password strength checked during registration.
- Prevent duplicate usernames or email.
- Prevent overbooking (no available slots).
- Prevent users from booking the same class multiple times.