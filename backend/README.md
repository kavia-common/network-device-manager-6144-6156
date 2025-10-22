# Network Device Manager - Backend

Flask backend providing CRUD APIs for devices, optional ping functionality, MongoDB persistence via pymongo, request validation with marshmallow, and OpenAPI docs via flask-smorest.

## Features
- CRUD endpoints under `/api/v1/devices`
- Optional `POST /api/v1/devices/<id>/ping` to update device status when `ENABLE_PING=true`
- Validation and standardized errors via marshmallow/flask-smorest
- MongoDB persistence using pymongo
- CORS enabled for `http://localhost:3000` by default
- OpenAPI served at `/docs` and generated to `interfaces/openapi.json`

## Requirements
- Python 3.10+
- A running MongoDB instance
- Environment variables (.env) — see `.env.example`

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Copy `.env.example` to `.env` and update values:
   - MONGODB_URI
   - MONGODB_DB
   - API_PREFIX (optional, default `/api/v1`)
   - PORT (optional, default `3001`)
   - ENABLE_PING (optional, default `true`)
   - CORS_ORIGINS (optional, default `http://localhost:3000`)
4. Run the server:
   python run.py

## Environment Variables
- FLASK_ENV: development | production
- PORT: default 3001
- API_PREFIX: default /api/v1
- MONGODB_URI: required
- MONGODB_DB: required
- ENABLE_PING: true/false (default true)
- CORS_ORIGINS: allowed origins (default http://localhost:3000)

If MONGODB_URI or MONGODB_DB are missing, the app will raise a clear error when first accessing the database.

## Endpoints (summary)
- GET / -> Health check
- GET /api/v1/devices -> List devices
- POST /api/v1/devices -> Create device
- GET /api/v1/devices/<id> -> Get device
- PUT /api/v1/devices/<id> -> Update device
- DELETE /api/v1/devices/<id> -> Delete device
- POST /api/v1/devices/<id>/ping -> Ping device (updates status if ENABLE_PING=true; returns note if disabled)

## OpenAPI
- Interactive docs at /docs
- Generate static spec:
  python generate_openapi.py
  The spec is saved to interfaces/openapi.json

## Notes
- Device schema fields: name, ip_address, type(router|switch|server), location, status(online|offline default offline), notes, created_at, updated_at. `_id` is exposed as `id` (string).
- Ping is implemented using `subprocess` for cross platform behavior.
