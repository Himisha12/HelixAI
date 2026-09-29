# OpenAPI Contract & API Reference

## Base URL
`http://localhost:8000/api/v1`

---

## 1. Authentication Endpoints

### `POST /auth/register`
Register a new user account.
- **Request Body**:
```json
{
  "username": "developer1",
  "email": "dev@example.com",
  "password": "secretpassword123"
}
```
- **Response (201 Created)**:
```json
{
  "id": "user-a1b2c3d4",
  "username": "developer1",
  "email": "dev@example.com",
  "role": "user",
  "is_active": true
}
```

### `POST /auth/token`
Obtain OAuth2 JWT access token.
- **Form Data**:
  - `username`: `demo_user`
  - `password`: `demo123`
- **Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer",
  "expires_in_seconds": 3600
}
```

### `GET /auth/me`
Retrieve user profile and sliding-window rate limit stats.
- **Headers**: `Authorization: Bearer <JWT_TOKEN>`
- **Response (200 OK)**:
```json
{
  "user": {
    "id": "user-12345678",
    "username": "demo_user",
    "email": "demo@ai-microservice.io",
    "role": "user",
    "is_active": true
  },
  "usage_metrics": {
    "current_rpm": 2,
    "max_rpm": 20,
    "current_tpm": 150,
    "max_tpm": 10000
  }
}
```

---

## 2. LLM Chat Completions Endpoint

### `POST /chat/completions`
Generate completion using open models.
- **Headers**: `Authorization: Bearer <JWT_TOKEN>`
- **Request Body**:
```json
{
  "model": "llama3-open-8b",
  "messages": [
    {"role": "system", "content": "You are a helpful coding assistant."},
    {"role": "user", "content": "Write a python hello world function."}
  ],
  "temperature": 0.7,
  "max_tokens": 256,
  "structured_json": false
}
```
- **Response (200 OK)**:
```json
{
  "id": "chatcmpl-a1b2c3d4e5f6",
  "object": "chat.completion",
  "created": 1727610000,
  "model": "llama3-open-8b",
  "backend": "local_fast_engine",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Here is a Python snippet:\n\n```python\ndef hello_world():\n    print('Hello World')\n```"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 22,
    "total_tokens": 37,
    "latency_ms": 12.4
  }
}
```

---

## 3. Tool Execution Endpoints

### `GET /tools`
List all registered AI tools.
- **Response (200 OK)**:
```json
[
  {
    "name": "calculator",
    "description": "Perform safe numerical evaluation",
    "parameters": {
      "expression": {"type": "string", "description": "Math string", "required": true}
    }
  }
]
```

### `POST /tools/execute`
Execute a bounded tool call.
- **Headers**: `Authorization: Bearer <JWT_TOKEN>`
- **Request Body**:
```json
{
  "tool_name": "calculator",
  "arguments": {
    "expression": "125 * 8 + 50"
  }
}
```
- **Response (200 OK)**:
```json
{
  "tool_name": "calculator",
  "status": "success",
  "result": {
    "expression": "125 * 8 + 50",
    "value": 1050
  },
  "error": null
}
```
