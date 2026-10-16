🐴 Neigh-ver Alone
==================

_Tinder for horses — find your perfect pasture partner._

A Flask-based dating platform where horses (and their humans) can create profiles, answer horse-specific personality questions, and get matched based on breed, discipline, temperament, region, and more.

## Features

- **User Registration** — Email/password signup or Google OAuth login
- **Horse Profiles** — Breed, discipline, temperament, ideal date activity, offspring goals, and more
- **Matching Algorithm** — Scores profiles 0-100% based on 10 weighted criteria
- **Swipe Interface** — Browse one at a time, like or pass with keyboard arrows (← →)
- **Mutual Matching** — When both horses like each other, it's a match with an icebreaker prompt
- **50 Seed Accounts** — Pre-populated with horse profiles and photos so the platform never feels empty

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Or: Python 3.11+ and PostgreSQL 16

### Run with Docker (Recommended)

```bash
docker-compose up --build
```

This will:
1. Start PostgreSQL
2. Build the Flask app
3. Auto-create database tables
4. Seed 50 horse profiles
5. Start the web server on port 5000

Visit **http://localhost:5000**

### Manual Setup

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL and create the database:
#   createdb horsetinder
#   createuser horseuser

cp .env.example .env
# Edit .env with your database URL and secret key

# Create tables
python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all()"

# Seed the database
python seed.py

# Run
flask run
```

## Seed Accounts

50 pre-made horse profiles are created with password `horselover123`.

| Email Range | Password |
|---|---|
| horse0@pasturematch.com — horse49@pasturematch.com | horselover123 |

## Google OAuth Setup

1. Go to https://console.cloud.google.com/apis/credentials
2. Create an OAuth 2.0 Client ID (Web application)
3. Add `http://localhost:5000/auth/google/callback` as an authorized redirect URI
4. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`

## Matching Criteria

| Factor | Weight | Description |
|---|---|---|
| Same Breed | 20 | Strong connection between same breeds |
| Same Discipline | 15 | Shared riding discipline |
| Same Temperament | 12 | Compatible personality types |
| Same Region | 10 | Live in the same area |
| Experience Level | 10 | Within 1 level of each other |
| Age Compatibility | 8 | Within 5 years of each other |
| Height Compatibility | 8 | Within 3 hands |
| Offspring Goals | 8 | Aligned on wanting foals |
| Ideal Date Overlap | 7 | Shared activity keywords |
| Coat Color Appeal | 2 | Different colors attract |

## Project Structure

```
horse-tinder/
├── app.py                 # Flask application factory
├── config.py              # Configuration
├── extensions.py          # SQLAlchemy, Migrate, LoginManager
├── models.py              # User, HorseProfile, Match models
├── auth.py                # Login, register, Google OAuth
├── profiles.py            # Create/edit horse profiles
├── matches.py             # Browse, swipe, matching algorithm
├── seed.py                # Generate 50 seed accounts
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── create_profile.html
    ├── browse.html
    ├── view_profile.html
    └── my_matches.html
```

## Tech Stack

- **Backend:** Flask (Python 3.11)
- **Database:** PostgreSQL 16
- **Auth:** Flask-Login + Google OAuth (Authlib)
- **Frontend:** Bootstrap 5, jQuery
- **Deployment:** Docker / Gunicorn
