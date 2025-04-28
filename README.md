# Study Session Tracker API Documentation

## Overview
This API provides a comprehensive system for tracking study sessions, grades, and user management for students and teachers. It includes authentication, user management, session tracking, grade management, and integration with ChatGPT.

## How to Run Locally
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

## Models

### Database Models

1. **User** (Base class)
   - `id`: Primary key
   - `first_name`: User's first name
   - `last_name`: User's last name
   - `user_type`: Enum (STUDENT or TEACHER)
   - Relationship with `UserAuth`

2. **Teacher** (extends User)
   - Relationship with assigned `Student`s
   - Relationship with `Grade`s given

3. **Student** (extends User)
   - `assigned_teacher_id`: Foreign key to Teacher
   - Relationship with `Session`s
   - Relationship with `Grade`s received

4. **Grade**
   - `date`: When grade was given
   - `graded_student_id`: Foreign key to Student
   - `grader_teacher_id`: Foreign key to Teacher
   - `score`: Numeric grade (0-100)
   - `comments`: Optional comments

5. **Session**
   - `date`: When session occurred
   - `student_id`: Foreign key to Student
   - `length_minutes`: Duration in minutes

6. **UserAuth**
   - Stores authentication credentials
   - `username`: Unique identifier
   - `password_hash`: Hashed password

### Pydantic Schemas (Request/Response Models)

1. **AuthRequest**: Login credentials
2. **AuthResponse**: JWT token response
3. **UserCreate**: Base user creation
4. **StudentCreate**: Student-specific creation
5. **GradeCreate**: Grade assignment data
6. **UserResponse**: Base user response
7. **StudentResponse**: Student-specific response
8. **GradeResponse**: Grade record response
9. **SessionRequest**: Session creation data
10. **SessionResponse**: Basic session response
11. **ChatRequest**: ChatGPT prompt
12. **ChatResponse**: ChatGPT response
13. **GradeFilter**: Grade query filters
14. **SessionFilter**: Session query filters
15. **SessionResponseExtended**: Session with student info

## API Endpoints

### Authentication

#### `POST /api/v1/authenticate`
- **Description**: Authenticate user and receive JWT token
- **Request Body**: `AuthRequest` (username, password)
- **Response**: `AuthResponse` (token, user_type)
- **Access**: Public

### User Management

#### `POST /api/v1/users`
- **Description**: Create new user (student or teacher)
- **Request Body**: `UserCreate` or `StudentCreate`
- **Response**: `UserResponse` or `StudentResponse`
- **Access**: Public
- **Notes**: Creates both User and UserAuth records

### Grade Management (Teacher Only)

#### `POST /api/v1/grades`
- **Description**: Create new grade record
- **Request Body**: `GradeCreate`
- **Response**: `GradeResponse`
- **Access**: Teacher only
- **Validations**:
  - Score must be between 0-100
  - Student must exist

#### `GET /api/v1/grades`
- **Description**: Get grades assigned by current teacher
- **Query Parameters**: Optional filters via `GradeFilter`
  - `student_id`, date range, score range
- **Response**: List of `GradeResponse`
- **Access**: Teacher only
- **Notes**: Automatically filters by teacher

### Session Management

#### `POST /api/v1/sessions`
- **Description**: Save study session
- **Request Body**: `SessionRequest`
- **Response**: `SessionResponse`
- **Access**: Student only
- **Validations**:
  - Student ID must match authenticated user

#### `GET /api/v1/teacher/sessions`
- **Description**: Get sessions for teacher's students
- **Query Parameters**: Optional filters via `SessionFilter`
  - `student_id`, date range, duration range
- **Response**: List of `SessionResponseExtended`
- **Access**: Teacher only
- **Notes**:
  - Includes student names
  - Only shows assigned students

### ChatGPT Integration

#### `POST /api/v1/chat`
- **Description**: Send prompt to ChatGPT
- **Request Body**: `ChatRequest`
- **Response**: `ChatResponse`
- **Access**: Student only

## Security

- JWT authentication (Bearer tokens)
- Password hashing (PBKDF2-SHA256)
- Role-based access control
- Token expiration (60 minutes)

## Error Handling

Common error responses:
- `401 Unauthorized`: Invalid/missing token
- `403 Forbidden`: Role mismatch
- `404 Not Found`: Resource not found
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: Database issues

## Usage Examples

1. **User Registration**:
```bash
POST /api/v1/users
{
  "first_name": "John",
  "last_name": "Doe",
  "username": "johndoe",
  "password": "secure123",
  "user_type": "student",
  "assigned_teacher_id": 1
}
```

2. **Authentication**:
```bash
POST /api/v1/authenticate
{
  "username": "johndoe",
  "password": "secure123"
}
```

3. **Create Grade (Teacher)**:
```bash
POST /api/v1/grades
Authorization: Bearer <token>
{
  "student_id": 1,
  "date": "2025-05-15T14:30:00Z",
  "score": 85.5,
  "comments": "Good work!"
}
```

4. **Get Sessions (Teacher)**:
```bash
GET /api/v1/teacher/sessions?start_date=2025-01-01&end_date=2025-01-31
Authorization: Bearer <token>
```

5. **Chat with AI**:
```bash
POST /api/v1/chat
Authorization: Bearer <token>
{
  "prompt": "Explain quantum physics simply"
}
```