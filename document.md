# Education ChatBot - API Documentation

## 1. Overview

This API provides authentication and chatbot query services for an education-focused chatbot. It uses FastAPI, JWT-based authentication, and vector-based similarity search for responses.

## 2. Authentication Service

### 2.1. Verify Request Signature

- **Endpoint:** `GET /authentication/rcsa-authentication`
- **Description:** Verifies the request signature before allowing access to protected routes.
- **Headers Required:**
  - `X-Signature`: Base64-encoded signature of the request.
- **Response:**
  - `200 OK`: `{ "message": "Authorized access!" }`
  - `401 Unauthorized`: `{ "detail": "Invalid key message." }`

### 2.2. Generate JWT Token

- **Endpoint:** `POST /authentication/generate-token`
- **Description:** Generates a JWT token with a time-to-live (TTL).
- **Headers Required:**
  - `X-Signature`: Base64-encoded request signature.
- **Response:**
  - `200 OK`: `{ "token": "your_jwt_token_here" }`
  - `500 Internal Server Error`: `{ "detail": "Internal server error" }`

## 3. Chatbot Query Service

### 3.1. Query Chatbot

- **Endpoint:** `POST /chatbot/query`
- **Description:** Processes user queries and retrieves relevant responses using vector-based semantic search.
- **Headers Required:**
  - `Authorization`: `Bearer <JWT Token>`
- **Request Body:**
  
  ```json
  {
    "query": "Your question here"
  }
  ```
  
- **Response:**
  
  ```json
  {
    "query": "Your question here",
    "result": "Chatbot response"
  }
  ```
  
- **Error Responses:**
  - `401 Unauthorized`: `{ "detail": "Token has expired" }`
  - `500 Internal Server Error`: `{ "detail": "Internal server error" }`

## 4. Authentication Module (EduAuthenticator)

### 4.1. JWT Authentication

- Generates and verifies JWT tokens using a secret key.
- Tokens have a fixed TTL (Time-to-Live).

### 4.2. RSA Encryption

- Uses RSA keys to encrypt and decrypt authentication data.
- **Methods:**
  - `encrypt(data: str) -> str`: Encrypts data with a public key.
  - `decrypt(encrypted_data: str) -> str`: Decrypts data with a private key.

### 4.3. Key Management

- Generates public and private key pairs.
- Saves them as `.pem` files.

## 5. Application Lifecycle (`app.py`)

### 5.1. Startup and Shutdown

#### Startup Actions:

- Loads authentication keys.
- Initializes vector database (DuckDB).
- Loads `intfloat/multilingual-e5-base` for embedding generation.

#### Shutdown Actions:

- Closes database connections.
- Runs garbage collection.

### 5.2. Middleware

- Adds request processing time in the response header (`X-Process-Time`).

### 5.3. Index Page

- **Endpoint:** `GET /`
- **Response:**
  
  ```html
  <html>
      <head>
          <title>Home</title>
      </head>
      <body>
          <h1>FastAPI</h1>
          <p>Swagger: /docs</p>
      </body>
  </html>
  ```

## 6. Technology Stack

- **FastAPI**: Web framework for building APIs.
- **DuckDB**: Vector database for semantic search.
- **intfloat/multilingual-e5-base**: Model used for question embedding and retrieval.
- **JWT**: Authentication and session management.
- **RSA Encryption**: Secure key-based authentication.