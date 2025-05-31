# User Authentication & Personal Finance API

This project provides a user authentication API and a personal finance management system using Django, Django REST Framework, and JWT (SimpleJWT).

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
  - **429 Too Many Requests**
    ```json
    { "detail": "Rate limit exceeded. Max 10 requests per 60 seconds." }
    ```

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
  - **429 Too Many Requests**
    ```json
    { "detail": "Rate limit exceeded. Max 10 requests per 60 seconds." }
    ```

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
  - **429 Too Many Requests**
    ```json
    { "detail": "Rate limit exceeded. Max 5 requests per 60 seconds." }
    ```

## CRUD API Endpoints (Authenticated)

All endpoints below require the `Authorization: Bearer <access_token>` header.

### Account Endpoints
- **List Accounts**
  - Method: GET
  - URL: `/api/accounts/`
  - **Rate Limit:** 10 requests per 60 seconds
- **Create Account**
  - Method: POST
  - URL: `/api/accounts/`
  - Request Body:
    ```json
    {
      "name": "Cash Wallet",
      "type": "cash",
      "balance": 100.00,
      "institution": "Home"
    }
    ```
- **Retrieve Account**
  - Method: GET
  - URL: `/api/accounts/{id}/`
- **Update Account**
  - Method: PUT/PATCH
  - URL: `/api/accounts/{id}/`
- **Delete Account**
  - Method: DELETE
  - URL: `/api/accounts/{id}/`
- **429 Too Many Requests**
  ```json
  { "detail": "Rate limit exceeded. Max 10 requests per 60 seconds." }
  ```

### Category Endpoints
- **List Categories**
  - Method: GET
  - URL: `/api/categories/`
  - **Rate Limit:** 10 requests per 60 seconds
- **Create Category**
  - Method: POST
  - URL: `/api/categories/`
  - Request Body:
    ```json
    {
      "name": "Food",
      "type": "expense",
      "description": "Groceries and dining out",
      "color": "#ff0000"
    }
    ```
- **Retrieve Category**
  - Method: GET
  - URL: `/api/categories/{id}/`
- **Update Category**
  - Method: PUT/PATCH
  - URL: `/api/categories/{id}/`
- **Delete Category**
  - Method: DELETE
  - URL: `/api/categories/{id}/`
- **429 Too Many Requests**
  ```json
  { "detail": "Rate limit exceeded. Max 10 requests per 60 seconds." }
  ```

### Transaction Endpoints
- **List Transactions**
  - Method: GET
  - URL: `/api/transactions/`
  - **Rate Limit:** 10 requests per 60 seconds
- **Create Transaction**
  - Method: POST
  - URL: `/api/transactions/`
  - Request Body:
    ```json
    {
      "account": 1,
      "category": 2,
      "amount": 50.00,
      "date": "2024-06-01",
      "description": "Grocery shopping",
      "is_income": false
    }
    ```
- **Retrieve Transaction**
  - Method: GET
  - URL: `/api/transactions/{id}/`
- **Update Transaction**
  - Method: PUT/PATCH
  - URL: `/api/transactions/{id}/`
- **Delete Transaction**
  - Method: DELETE
  - URL: `/api/transactions/{id}/`
- **429 Too Many Requests**
  ```json
  { "detail": "Rate limit exceeded. Max 10 requests per 60 seconds." }
  ```

**All requests must include:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Error Handling:**
- 401 Unauthorized: If token is missing or invalid
- 400 Bad Request: For invalid data
- 404 Not Found: If resource does not exist
- 429 Too Many Requests: If rate limit is exceeded

## Rate Limiting
- **Register & Login:** 10 requests per 60 seconds per user/IP
- **Protected Route:** 5 requests per 60 seconds per user/IP
- **Account, Category, Transaction CRUD:** 10 requests per 60 seconds per user/IP
- If the limit is exceeded, a 429 response is returned:
  ```json
  { "detail": "Rate limit exceeded. Max <limit> requests per <period> seconds." }
  ```

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
- Proper error handling is implemented for invalid credentials, unauthorized access, and rate limiting. 