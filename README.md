# Job Application Tracker API

## Project Overview
Job Application Tracker API is a FastAPI backend for managing a personal job search workflow. It provides JWT-based authentication and endpoints for tracking companies, applications, and interview rounds, with database migrations, automated tests, Docker support, and CI ready to go.

## Features
- User registration and login with JWT authentication
- Company CRUD scoped to the authenticated user
- Application CRUD scoped to the authenticated user
- Interview tracking nested under applications
- Application filtering and pagination
- Status transition validation for applications
- Alembic database migrations
- Pytest test suite
- Docker and Docker Compose setup
- GitHub Actions CI workflow

## Stack
| Category | Technology |
| --- | --- |
| Language | Python 3.12 |
| Framework | FastAPI |
| DB | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | JWT with `python-jose`, password hashing with `bcrypt` |
| Testing | Pytest, FastAPI TestClient, HTTPX |
| Linting | Ruff |
| Container | Docker, Docker Compose |
| CI | GitHub Actions |

## Local Setup
1. Clone the repository.
   ```bash
   git clone https://github.com/atharva6905/job-tracker-api.git
   cd job-tracker-api
   ```
2. Copy the example environment file.
   ```bash
   cp .env.example .env
   ```
3. Fill in the values in `.env` (see Environment Variables below).
4. Start dependencies.
   ```bash
   docker compose up -d postgres
   ```
5. Install dependencies locally.
   ```bash
   pip install ".[dev]"
   ```
6. Run migrations.
   ```bash
   alembic upgrade head
   ```
7. Start the API server.
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
8. Open the interactive docs at `http://localhost:8000/docs`.

Optional full Docker run:
```bash
docker compose up --build
```

## Environment Variables
| Variable | Description | Example |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL connection string for the app database | `postgresql://tracker:tracker@localhost:5432/tracker` |
| `SECRET_KEY` | Secret used to sign JWT access tokens | `change-me-to-a-long-random-secret-key` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes | `30` |


## Migrations
Run the latest migrations with:

```bash
alembic upgrade head
```

## Tests
Run the test suite with:

```bash
pytest -v
```

## API Routes
| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | No | Health check endpoint |
| `POST` | `/auth/register` | No | Register a new user |
| `POST` | `/auth/login` | No | Log in and receive a JWT access token |
| `GET` | `/auth/me` | Yes | Return the current authenticated user |
| `GET` | `/companies/` | Yes | List the current user's companies |
| `POST` | `/companies/` | Yes | Create a company for the current user |
| `GET` | `/companies/{company_id}` | Yes | Fetch one owned company |
| `PATCH` | `/companies/{company_id}` | Yes | Partially update one owned company |
| `DELETE` | `/companies/{company_id}` | Yes | Delete one owned company |
| `GET` | `/applications/` | Yes | List owned applications with filters and pagination |
| `POST` | `/applications/` | Yes | Create an application under an owned company |
| `GET` | `/applications/{app_id}` | Yes | Fetch one owned application |
| `PATCH` | `/applications/{app_id}` | Yes | Partially update one owned application |
| `DELETE` | `/applications/{app_id}` | Yes | Delete one owned application |
| `POST` | `/applications/{app_id}/interviews/` | Yes | Create an interview for an owned application |
| `GET` | `/applications/{app_id}/interviews/` | Yes | List interviews for an owned application |

## Deployment Notes
- Platforms such as Render, Railway, and Fly.io can run this app with a managed PostgreSQL database.
- Set the required environment variables: `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Run `alembic upgrade head` during deploy or at container start before serving traffic.
- Start the app with:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

## ER Diagram
```mermaid
erDiagram
    USER ||--o{ COMPANY : owns
    USER ||--o{ APPLICATION : owns
    COMPANY ||--o{ APPLICATION : has
    APPLICATION ||--o{ INTERVIEW : has

    USER {
        int id PK
        string email
        string hashed_password
        datetime created_at
    }

    COMPANY {
        int id PK
        int user_id FK
        string name
        string location
        string link
        datetime created_at
    }

    APPLICATION {
        int id PK
        int user_id FK
        int company_id FK
        string role
        string status
        date date_applied
        text notes
        datetime created_at
    }

    INTERVIEW {
        int id PK
        int application_id FK
        string round_type
        datetime scheduled_at
        string outcome
        text notes
        datetime created_at
    }
```
