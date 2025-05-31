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

## CRUD API Endpoints (Authenticated)

All endpoints below require the `Authorization: Bearer <access_token>` header.

### Author Endpoints
- **List Authors**
  - Method: GET
  - URL: `/api/authors/`
  - Response: 200 OK
    ```json
    [
      {
        "id": 1,
        "name": "Author Name",
        "birth_date": "1970-01-01",
        "nationality": "Country",
        "biography": "Bio...",
        "email": "author@email.com"
      }
    ]
    ```
- **Create Author**
  - Method: POST
  - URL: `/api/authors/`
  - Request Body:
    ```json
    {
      "name": "Author Name",
      "birth_date": "1970-01-01",
      "nationality": "Country",
      "biography": "Bio...",
      "email": "author@email.com"
    }
    ```
- **Retrieve Author**
  - Method: GET
  - URL: `/api/authors/{id}/`
- **Update Author**
  - Method: PUT/PATCH
  - URL: `/api/authors/{id}/`
- **Delete Author**
  - Method: DELETE
  - URL: `/api/authors/{id}/`

### Publisher Endpoints
- **List Publishers**
  - Method: GET
  - URL: `/api/publishers/`
- **Create Publisher**
  - Method: POST
  - URL: `/api/publishers/`
  - Request Body:
    ```json
    {
      "name": "Publisher Name",
      "address": "123 Main St",
      "website": "https://example.com",
      "contact_email": "contact@example.com",
      "established_year": 2000
    }
    ```
- **Retrieve Publisher**
  - Method: GET
  - URL: `/api/publishers/{id}/`
- **Update Publisher**
  - Method: PUT/PATCH
  - URL: `/api/publishers/{id}/`
- **Delete Publisher**
  - Method: DELETE
  - URL: `/api/publishers/{id}/`

### Book Endpoints
- **List Books**
  - Method: GET
  - URL: `/api/books/`
- **Create Book**
  - Method: POST
  - URL: `/api/books/`
  - Request Body:
    ```json
    {
      "title": "Book Title",
      "author": 1,
      "publisher": 1,
      "publication_date": "2024-01-01",
      "isbn": "1234567890123",
      "summary": "Book summary..."
    }
    ```
- **Retrieve Book**
  - Method: GET
  - URL: `/api/books/{id}/`
- **Update Book**
  - Method: PUT/PATCH
  - URL: `/api/books/{id}/`
- **Delete Book**
  - Method: DELETE
  - URL: `/api/books/{id}/`

**All requests must include:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Error Handling:**
- 401 Unauthorized: If token is missing or invalid
- 400 Bad Request: For invalid data
- 404 Not Found: If resource does not exist

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