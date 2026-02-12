# Authentication Usage Guide

## Overview
The Book Haven API now includes JWT-based authentication with user registration and login functionality.

## Authentication Endpoints

### 1. Register a New User
**POST** `/api/users/register`

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "city": "New York",
  "country": "USA"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user",
    "full_name": "John Doe",
    "city": "New York",
    "country": "USA"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "User registered successfully"
}
```

**Validation Rules:**
- Username: 3-50 characters, alphanumeric and underscores only
- Email: Valid email format
- Password: Minimum 8 characters, at least one uppercase, one lowercase, and one number

---

### 2. Login
**POST** `/api/users/login`

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "SecurePass123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user",
    "full_name": "John Doe",
    "city": "New York",
    "country": "USA"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Login successful"
}
```

---

### 3. Get Current User Info
**GET** `/api/users/me`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "user",
  "full_name": "John Doe",
  "city": "New York",
  "country": "USA"
}
```

---

### 4. Update Current User Info
**PUT/PATCH** `/api/users/me`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Request Body:**
```json
{
  "full_name": "John Smith",
  "city": "Los Angeles"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "user",
  "full_name": "John Smith",
  "city": "Los Angeles",
  "country": "USA"
}
```

---

## Protected Routes

### Admin-Only Routes
The following routes require admin role:
- `GET /api/users` - List all users
- `POST /api/users` - Create user (admin)
- `PUT/PATCH /api/users/<id>` - Update any user
- `DELETE /api/users/<id>` - Delete user

### Authenticated Routes
These routes require a valid token:
- `GET /api/users/<id>` - Get user by ID
- `GET /api/users/me` - Get current user
- `PUT/PATCH /api/users/me` - Update current user

---

## Using Authentication in Code

### Protecting Routes with @token_required
```python
from app.utils.auth import token_required

@app.route('/protected')
@token_required
def protected_route():
    # Access current user info
    user_id = request.current_user.get('user_id')
    username = request.current_user.get('username')
    return jsonify({'message': f'Hello {username}'})
```

### Protecting Routes with @role_required
```python
from app.utils.auth import role_required

@app.route('/admin-only')
@role_required('admin')
def admin_route():
    return jsonify({'message': 'Admin access granted'})

@app.route('/staff-only')
@role_required('admin', 'moderator')
def staff_route():
    return jsonify({'message': 'Staff access granted'})
```

### Getting Current User
```python
from app.utils.auth import get_current_user

@app.route('/profile')
@token_required
def profile():
    user = get_current_user()
    return jsonify(user)
```

---

## Testing with cURL

### Register
```bash
curl -X POST http://localhost:5000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123"
  }'
```

### Access Protected Route
```bash
curl -X GET http://localhost:5000/api/users/me \
  -H "Authorization: Bearer <your_token_here>"
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields: username, password"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication token is missing"
}
```

```json
{
  "error": "Invalid username or password"
}
```

### 403 Forbidden
```json
{
  "error": "Insufficient permissions"
}
```

---

## Token Information
- Tokens are valid for **7 days** from issuance
- Tokens are signed with HS256 algorithm
- Token payload includes: user_id, username, role, exp (expiration), iat (issued at)
