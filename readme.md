# Cab App

Cab app is a basic django application which provide REST api for cab booking system
loosely inspired by cab services like ola/uber.

## Features:
  - Registration for new user and new dirver.
  - User can book a cab if available.
  - One user can only book one cab at a time.
  - Two user can't book the same cab at the same time.
  - User/Driver can see there rides history.
  - User can also book a sharing cab.

### Installation

Cab service requires [Python](https://docs.python.org/3.6/) v3.6+ to run.

Create python3 virtual env and install the dependencies,
migrate database and start the server.

```sh
$ git clone git@gitlab.com:gouravtulsani/cab-app-backend.git
$ cd cab-app-backend/
$ python3 -m venv .
$ pip install -r requirments.txt
$ cd src/
$ python manage.py migrate && python manage.py runserver
```

## APIs

### Registration
- API description:
    > This api is use to register a new customer/driver
- Request Headers:
    - Request URL: **/api/register**
    - Supported Request Methods: POST
    - Content-Type: application/json
- Example api request
```json
    {
        "username": "<username>" "(unique)",
        "password": "<password>",
        "first_name": "<firstname>",
        "last_name": "<lastname>",
        "email": "<email address>" "(unique)",
        "phone_number": "<ph_number>" "(var char len(10), unique)",
        "is_driver": "<true/false>",
        "car_model": "<car model>" "(required if is_driver is true)",
        "car_number": "<car number>" "(required if is_driver is true)"
    }
```
- Response headers:
- Status ``200``:
    - Content-Type: application/json
    - Response Body: *driver/customer registered successfully*
    - Conditions for Success:
        - All input validations are successful and user has
        been successfully been registered.
- Status ``400``:
    - Content-Type: application/json
    - Response Body: *text message indicating reason for failure*
    - Conditions for Failure:
        - username/email/phone_number/car_details already

### Login
- API description:
    > This api is use to login into the app
      and after successful login you'll get 
      token which you'll use for authentication
- Request Headers:
    - Request URL: **/api/complete_ride**
    - Supported Request Methods: POST
    - Content-Type: application/json
- Example api request
```json
    {
        "username": "<username>" "(required)",
        "password": "<password>" "(required)"
    }
```
- Response headers:
- Status ``200``:
    - Content-Type: application/json
    - Response Body: *login successfully*
    - Conditions for Success:
        - Only if the input username and password is valid.
- Status ``400``:
    - Content-Type: application/json
    - Response Body: *text message indicating reason for failure*
    - Conditions for Failure:
        - username or password is incorrect

### Logout
- API description:
    > This api is use to logout from the app
      Token authentication required
- Request Headers:
    - Request URL: **/api/complete_ride**
    - Supported Request Methods: GET
    - Content-Type: application/json
- Response headers:
- Status ``200``:
    - Content-Type: application/json
    - Response Body: *logout successfully*
    - Conditions for Success:
        - Only if the user is authenticated.
- Status ``400``:
    - Content-Type: application/json
    - Response Body: *text message indicating reason for failure*
    - Conditions for Failure:
        - authentication credentials not provided
        - invalid token


### Book ride
- API description:
    > This api is use to book a new ride.
    Only a customer can book a new ride, if there is no pending ride.
    Token authentication required

- Request Headers:
    - Request URL: **/api/book_ride**
    - Supported Request Methods: POST
    - Content-Type: application/json
- Example api request
```json
    {
        "ride_from": "<ride from>" "(required)",
        "ride_to": "<ride to>" "(required)",
        "sharing": "<true or false>" "(required)",
        "seats": "<1 or 2>" "(required if sharing is true)"
    }
```
- Response headers:
- Status ``200``:
    - Content-Type: application/json
    - Response Body: *Cab booked successfully/No free dirver available*
    - Conditions for Success:
        - All input validations are successful.
- Status ``400``:
    - Content-Type: application/json
    - Response Body: *text message indicating reason for failure*
    - Conditions for Failure:
        - requesting user is a driver
        - requesting user has already a ride in progress

### Complete ride
- API description:
    > This api is use to complete the existing ride
    only a driver can complete the ride
    Token authentication required
- Request Headers:
    - Request URL: **/api/complete_ride**
    - Supported Request Methods: POST
    - Content-Type: application/json
- Example api request
```json
    {
        "customer_name": "<customer username>" "(required)"
    }
```
- Response headers:
- Status ``200``:
    - Content-Type: application/json
    - Response Body: *ride completed successfully*
    - Conditions for Success:
        - Only if the driver have a existing incomplete ride.
- Status ``400``:
    - Content-Type: application/json
    - Response Body: *text message indicating reason for failure*
    - Conditions for Failure:
        - requesting user is a customer not driver
        - No on going ride

### Get ride history
- API description:
    > This api is use to get the ride history of the requesting user
      Token authentication required
- Request Headers:
    - Request URL: **/api/get_ride_history**
    - Supported Request Methods: GET
    - Content-Type: application/json
- Response headers:
- Status ``200``:
    - Content-Type: application/json
    - Response Body: *[{
        "id": <ride_id>,
        "ride_from": <from>,
        "ride_to": <to>,
        "ride_time": <ride start time>,
        "complete": false
    }...]*
    - Conditions for Success:
        - Only if requesting user is a valid user.
- Status ``400``:
    - Content-Type: application/json
    - Response Body: *text message indicating reason for failure*
    - Conditions for Failure:
        - Invalid username/password.
        - user not exists
