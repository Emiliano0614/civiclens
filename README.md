# CivicLens

A civic transparency platform for tracking local government hearings, public comments, and accountability summaries. Built with Flask, SQLAlchemy, and Groq for AI-assisted summarization.

## Stack

- **Backend:** Python, Flask, SQLAlchemy
- **Database:** PostgreSQL
- **AI:** Groq API for hearing/comment summarization
- **Data source:** YouTube Transcript API for synced hearing content

## Local Development (Docker)

The app is fully containerized and runs locally with a single command.

**Requirements:** Docker Desktop installed and running.

```bash
git clone https://github.com/Emiliano0614/civiclens.git
cd civiclens
```

Create a `.env` file in the project root with:

```
SECRET_KEY=your-secret-key
GROQ_API_KEY=your-groq-api-key
YOUTUBE_API_KEY=your-youtube-api-key
```

Then build and run:

```bash
docker compose up --build
```

This spins up two containers:
- `web` — the Flask app, served via Gunicorn on port 5000 (mapped to `localhost:5001`)
- `db` — a Postgres 16 instance with a persistent volume

Visit `http://localhost:5001` once both containers are up.

To seed an admin user:

```bash
docker compose exec web flask seed-admin
```

To stop:

```bash
docker compose down
```

## Deployment

Live on Render: **https://civiclens-e53x.onrender.com**

- Web service: Dockerized Flask app on Render's free tier
- Database: Render-managed Postgres (free tier)

Note: the free-tier database and web service both expire/spin down under Render's free plan limits (DB after 90 days, web service sleeps after inactivity and wakes on the next request with a short delay). Fine for a portfolio project; would need a paid tier for a permanent, always-on deployment.

## CI/CD

- **CI:** GitHub Actions (`.github/workflows/ci.yml`) runs on every push — installs dependencies, checks all Python files compile, and lints for critical errors (undefined names, syntax issues) via flake8.
- **CD:** Render auto-deploys on every push to `master`.

## Status

- [x] Core app (models, routes, auth, YouTube sync, AI summarization)
- [x] Dockerized with Docker Compose (Flask + Postgres)
- [x] Live deployment (Render)
- [x] CI/CD pipeline (GitHub Actions + Render auto-deploy)