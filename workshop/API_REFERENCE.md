# API Reference

## Authentication

All endpoints except `/register` and `/` require authentication via the `X-Service-Key` header.

```
X-Service-Key: <your-key>
```

---

## Endpoints

### `POST /register`

Register a new user and receive an authentication key.

**Request Body:**
```json
{
  "name": "string"
}
```

**Response:**
```json
{
  "status": "ok",
  "key": "uuid-string"
}
```

**Status Codes:**
- `200` - Success
- `400` - Missing name

---

### `POST /enqueue`

Add a document to your queue.

**Headers:**
- `X-Service-Key` (required)

**Request Body:**
```json
{
  // Any valid JSON document
}
```

**Response:**
```json
{
  "status": "ok",
  "queued_count": 5
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized or invalid key

---

### `GET /dequeue`

Retrieve and remove the oldest document from your queue.

**Headers:**
- `X-Service-Key` (required)

**Response:**
```json
{
  "document": {
    // The document that was queued
  }
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized or invalid key
- `404` - Queue empty

---

### `GET /peek`

View all documents in your queue without removing them.

**Headers:**
- `X-Service-Key` (required)

**Response:**
```json
{
  "queued_count": 3,
  "items": [
    // Array of queued documents
  ]
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized or invalid key

---

### `DELETE /clear`

Remove all documents from your queue.

**Headers:**
- `X-Service-Key` (required)

**Response:**
```json
{
  "status": "cleared"
}
```

**Status Codes:**
- `200` - Success
- `401` - Unauthorized or invalid key

---

### `GET /`

Health check endpoint.

**Response:**
```
Hello world
```

**Status Codes:**
- `200` - Success
