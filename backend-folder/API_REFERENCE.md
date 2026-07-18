# Quick Reference - JWT Authentication API

## Base URL
```
http://127.0.0.1:8000
```

## Endpoints

### 1. Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}

Response (201 CREATED):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "6a5a14b181367f954b98f84f",
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2026-07-17T11:40:33.658951"
  }
}

Errors:
- 409: Email already exists
- 400: Validation error
- 500: Server error
```

### 2. Login User
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123"
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "6a5a14b181367f954b98f84f",
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2026-07-17T11:40:33.658000"
  }
}

Errors:
- 401: Invalid email or password
- 500: Server error
```

## Using the Access Token

```
GET /api/protected-route
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## Password Requirements

- Minimum length: 8 characters
- Maximum length: 72 bytes (bcrypt limitation)
- No specific character requirements

## Email Requirements

- Must be valid email format
- Minimum length: 5 characters
- Must be unique (cannot register twice with same email)

## Username Requirements

- Minimum length: 3 characters
- Any characters allowed

## Token Information

- **Type**: JWT (JSON Web Token)
- **Algorithm**: HS256
- **Expiration**: 24 hours (configurable in .env)
- **Subject**: User's email

## Example Using curl

### Register
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

## Example Using Python

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# Register
response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "username": "john_doe",
        "email": "john@example.com",
        "password": "SecurePass123"
    }
)
print(response.json())

# Login
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "email": "john@example.com",
        "password": "SecurePass123"
    }
)
auth_data = response.json()
access_token = auth_data["access_token"]

# Use token
headers = {"Authorization": f"Bearer {access_token}"}
# response = requests.get(f"{BASE_URL}/api/protected", headers=headers)
```

## MongoDB Collection Schema

```javascript
db.users.insertOne({
  "_id": ObjectId,
  "username": "string",
  "email": "string (unique index recommended)",
  "password": "bcrypt hash string",
  "created_at": ISODate
})
```

## Environment Variables

```
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
DATABASE_NAME=PulseDrive
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## Status Codes

| Code | Meaning | Endpoint |
|------|---------|----------|
| 201 | Created | POST /register |
| 200 | OK | POST /login |
| 400 | Bad Request | Both |
| 401 | Unauthorized | /login |
| 409 | Conflict | /register (duplicate email) |
| 500 | Server Error | Both |

## Security Notes

✅ Passwords are hashed with bcrypt and never stored in plain text
✅ JWT tokens expire after 24 hours
✅ Password verification uses constant-time comparison
✅ Email uniqueness is enforced
✅ Passwords are never returned in responses
✅ Invalid login returns generic error (prevents user enumeration)

## Next Steps

### For Protected Routes:
1. Extract JWT from Authorization header
2. Verify token signature and expiration
3. Extract email (subject) from token
4. Lookup user in MongoDB
5. Proceed with request

### Middleware Example (FastAPI):
```python
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from app.config.settings import settings

async def get_current_user(token: str = Depends(HTTPBearer())):
    try:
        payload = jwt.decode(
            token.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)
    return email
```
