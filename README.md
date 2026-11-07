# URL Shortener Service

A backend service built to practise clean, production-style architecture: create short links, redirect quickly through a cache in front of the database, track clicks, and run the whole stack in containers.

## What it does

- **Shorten links:** create a short code for any URL through a REST API.
- **Fast redirects:** look-ups go through a Redis cache first and fall back to PostgreSQL.
- **Click analytics:** every redirect is counted, so you can see how each link is used.
- **Clean removal:** deleting a link also clears it from the cache.

## How it is built

- **FastAPI** application with a layered design: API routes, a service layer for business logic, and a repository layer for data access.
- **PostgreSQL** with **SQLAlchemy** models and **Alembic** migrations.
- **Redis** read-through cache for redirects.
- **Docker Compose** to run the API, database and cache together.

## Run locally

```bash
docker compose up --build
```

The API documentation is then available at `http://localhost:8000/docs`.

---

Built by [Shriram R](https://www.linkedin.com/in/shriram2008/) · [More projects](https://github.com/UniversalCodeBin)
