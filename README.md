# User Authentication API

This project provides a basic user authentication API using Django, Django REST Framework, and JWT (SimpleJWT).

## API Endpoints

### 1. Register
- **Method:** POST
- **URL:** `/api/register/`
- **Request Body:**
  ```json
  {
    "username": "yourusername",
    "password": "yourpassword",
    "email": "youremail@example.com"
  }
  ```
- **Response:**
  - **201 Created**
    ```json
    { "message": "User registered successfully." }
    ```
  - **400 Bad Request** (validation errors)

### 2. Login (Obtain JWT Token)
- **Method:** POST
- **URL:** `/api/login/`
- **Request Body:**
  ```json
  {
    "username": "yourusername",
    "password": "yourpassword"
  }
  ```
- **Response:**
  - **200 OK**
    ```json
    {
      "refresh": "<refresh_token>",
      "access": "<access_token>"
    }
    ```
  - **401 Unauthorized** (invalid credentials)

### 3. Protected Route
- **Method:** GET
- **URL:** `/api/protected/`
- **Headers:**
  - `Authorization: Bearer <access_token>`
- **Response:**
  - **200 OK**
    ```json
    { "message": "Hello, <username>! This is a protected route." }
    ```
  - **401 Unauthorized** (missing or invalid token)

## Setup
1. Install dependencies:
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt
   ```
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Start the server:
   ```bash
   python manage.py runserver
   ```

## Notes
- Passwords are securely hashed before storage.
- JWT tokens are used for authentication.
- Proper error handling is implemented for invalid credentials and unauthorized access. 