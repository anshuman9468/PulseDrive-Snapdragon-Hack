# Code Structure and File Organization

## Project Structure After Implementation

```
PulseDrive/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                    ✅ UPDATED
│   │   │   ├── health.py
│   │   │   ├── ask_ai.py
│   │   │   ├── prediction.py
│   │   │   └── sensor.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py            ✅ IMPLEMENTED
│   │   │   ├── prediction_service.py
│   │   │   └── sensor_service.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                    ✅ KEPT UNCHANGED
│   │   │   ├── alert.py
│   │   │   ├── prediction.py
│   │   │   └── sensor.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py                ✅ USED
│   │   │   └── database.py                ✅ USED
│   │   ├── utils/
│   │   ├── websocket/
│   │   ├── __init__.py
│   │   └── main.py                        ✅ ROUTER CONFIGURED
│   ├── requirements.txt                   ✅ ALL DEPENDENCIES
│   └── .env                               ✅ CONFIGURED
│
├── AUTHENTICATION_IMPLEMENTATION.md       ✅ CREATED
├── IMPLEMENTATION_CHECKLIST.md            ✅ CREATED
├── API_REFERENCE.md                       ✅ CREATED
└── CODE_STRUCTURE.md                      ✅ THIS FILE
```

## Key Implementation Files

### 1. app/services/auth_service.py (NEW IMPLEMENTATION)

**Purpose**: Core authentication business logic
**Lines of Code**: 107

**Key Components**:

```python
class AuthService:
    
    # Instance Variables
    self.db                    # MongoDB database
    self.users_collection      # MongoDB users collection
    
    # Core Methods
    hash_password()            # Bcrypt password hashing
    verify_password()          # Password verification
    create_access_token()      # JWT token generation
    create_user()              # User registration logic
    authenticate_user()        # User login logic
```

**Dependencies Imported**:
- `datetime` - For timestamps and token expiration
- `jose` - For JWT encoding/decoding
- `passlib` - For password hashing
- `pymongo` - For database operations
- `app.config` - For settings and database
- `app.models` - For Pydantic models

**Error Handling**:
- Raises `ValueError` for business logic errors
- Service layer lets API layer handle HTTP responses

### 2. app/api/auth.py (UPDATED)

**Purpose**: HTTP endpoints for authentication
**Lines of Code**: 72

**Endpoints**:
```python
@router.post("/register", status_code=201)
async def register(user: UserCreate) -> AuthResponse

@router.post("/login")
async def login(credentials: UserLogin) -> AuthResponse
```

**Error Handling**:
- 201: Successful registration
- 200: Successful login
- 400: Validation/bad request errors
- 401: Invalid credentials
- 409: Duplicate email
- 500: Server errors

**Request-Response Flow**:
1. Receive Pydantic-validated request
2. Call AuthService methods
3. Handle ValueError exceptions
4. Return HTTPException with appropriate status
5. Return AuthResponse with JWT token

### 3. app/models/user.py (UNCHANGED)

**Pydantic Models**:
```python
class UserBase:
    - username: str (min 3 chars)
    - email: str (min 5 chars)

class UserCreate(UserBase):
    - password: str (min 8 chars, max 72 bytes)

class UserLogin:
    - email: str
    - password: str

class UserResponse(UserBase):
    - id: str (MongoDB ObjectId as string)
    - created_at: datetime

class AuthResponse:
    - access_token: str
    - token_type: str
    - user: UserResponse
```

### 4. app/config/settings.py (USED)

**Configuration Source**:
```python
class Settings:
    MONGO_URI               # From .env
    DATABASE_NAME           # From .env
    SECRET_KEY              # From .env
    ALGORITHM               # From .env (HS256)
    ACCESS_TOKEN_EXPIRE_MINUTES  # From .env (1440)
```

### 5. app/config/database.py (USED)

**Database Connection**:
```python
get_client()    # Singleton MongoDB client
get_database()  # Singleton database instance
```

### 6. app/main.py (ROUTER CONFIG)

**Router Registration**:
```python
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
```

## Data Flow Diagrams

### Registration Flow

```
┌─────────────────────────────────────────────────────────┐
│ HTTP Request: POST /api/auth/register                  │
│ {username, email, password}                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────────────┐
│ Pydantic Validation (UserCreate)                        │
│ - username: min 3 chars                                 │
│ - email: min 5 chars                                    │
│ - password: min 8 chars, max 72 bytes                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────────────┐
│ API Route: auth.register()                              │
│ - Call AuthService.create_user()                        │
│ - Call AuthService.create_access_token()                │
│ - Handle errors and exceptions                          │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────────────┐
│ Service Layer: AuthService.create_user()                │
│ 1. Check if email exists in MongoDB                     │
│    └─ If yes → raise ValueError("Email already exists") │
│ 2. Hash password with bcrypt                            │
│ 3. Create user document                                 │
│ 4. Insert into MongoDB users collection                 │
│ 5. Return UserResponse (no password)                    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────────────┐
│ Service Layer: AuthService.create_access_token()        │
│ 1. Get expiration time from settings                    │
│ 2. Create JWT payload with email as subject             │
│ 3. Encode JWT with SECRET_KEY and ALGORITHM             │
│ 4. Return JWT token string                              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────────────┐
│ API Response: AuthResponse                              │
│ HTTP 201 Created                                        │
│ {access_token, token_type: "bearer", user}              │
└──────────────────────────────────────────────────────────┘
```

### Login Flow

```
┌─────────────────────────────────────────────────────────┐
│ HTTP Request: POST /api/auth/login                      │
│ {email, password}                                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────────────┐
│ Pydantic Validation (UserLogin)                         │
│ - email: min 5 chars                                    │
│ - password: min 8 chars                                 │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────────────┐
│ API Route: auth.login()                                 │
│ - Call AuthService.authenticate_user()                  │
│ - Handle errors and exceptions                          │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────────────┐
│ Service Layer: AuthService.authenticate_user()          │
│ 1. Query MongoDB for user by email                      │
│    └─ If not found → raise ValueError(generic error)    │
│ 2. Verify password with bcrypt                          │
│    └─ If wrong → raise ValueError(generic error)        │
│ 3. Create JWT access token                              │
│ 4. Create UserResponse (no password)                    │
│ 5. Return (token, user_response)                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────────────┐
│ API Response: AuthResponse                              │
│ HTTP 200 OK                                             │
│ {access_token, token_type: "bearer", user}              │
└──────────────────────────────────────────────────────────┘
```

## Database Schema

### MongoDB Collection: users

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "username": "john_doe",
  "email": "john@example.com",
  "password": "$2b$12$...",  // bcrypt hash
  "created_at": ISODate("2026-07-17T11:40:33.658Z")
}
```

**Indexes (Recommended)**:
```javascript
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ created_at: -1 })
```

## Password Hashing Details

**Algorithm**: bcrypt
**Cost Factor**: Default (12)
**Salt**: Automatically generated per password
**Hash Length**: 60 characters (starts with `$2b$`)

**Example Hash**:
```
$2b$12$K9h/cIPz0gi.URNNGLVB2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMUe
│││ │  │
│││ │  └─ Salt + hash (49 chars)
│││ └────── Cost factor (12)
││└──────── bcrypt algorithm (2b)
└┴────────── Salt (22 chars)
```

## JWT Token Structure

**Format**: Header.Payload.Signature

```json
// Header
{
  "alg": "HS256",
  "typ": "JWT"
}

// Payload
{
  "sub": "john@example.com",  // Subject (email)
  "exp": 1721234633,          // Expiration timestamp
  "iat": 1721148233           // Issued at timestamp
}

// Signature
HMACSHA256(
  base64UrlEncode(header) + "." +
  base64UrlEncode(payload),
  secret_key
)
```

## Environment Configuration

**.env file**:
```
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/
DATABASE_NAME=PulseDrive
SECRET_KEY=pulsedrive123
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## Dependencies and Versions

```
fastapi                 - Web framework
uvicorn                 - ASGI server
pymongo                 - MongoDB driver
pydantic                - Data validation
python-dotenv           - Environment variables
python-jose[crypto]     - JWT handling
passlib[bcrypt]         - Password hashing (4.3.0)
bcrypt                  - Bcrypt library (4.3.0)
websockets              - WebSocket support
python-multipart        - Form data parsing
```

## Error Handling Strategy

### Service Layer (auth_service.py)
- Raises `ValueError` for validation errors
- Lets exceptions propagate naturally
- No HTTP awareness

### API Layer (auth.py)
- Catches `ValueError` exceptions
- Converts to appropriate HTTPException
- Maps to correct HTTP status codes

### Error Response Format
```json
{
  "detail": "Error message or description"
}
```

## Testing Summary

All endpoints tested with:
1. ✅ Valid user registration
2. ✅ JWT token generation
3. ✅ Valid user login
4. ✅ Duplicate email prevention (409)
5. ✅ Invalid password rejection (401)
6. ✅ Proper status codes
7. ✅ No password leakage

## Future Enhancements

### Authentication
- [ ] Token refresh endpoint
- [ ] Token revocation/blacklist
- [ ] Email verification
- [ ] Password reset flow

### Security
- [ ] Rate limiting
- [ ] CORS refinement
- [ ] HTTPS enforcement
- [ ] Security headers

### Features
- [ ] Role-based access control (RBAC)
- [ ] Multi-factor authentication (MFA)
- [ ] Social login integration
- [ ] Account lockout on failed attempts

### Monitoring
- [ ] Authentication logs
- [ ] Failed login attempts tracking
- [ ] Token usage monitoring
- [ ] Security alerts
