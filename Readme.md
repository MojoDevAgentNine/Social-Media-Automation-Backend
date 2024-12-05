```markdown
backend
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│
├── app/
│   ├── axiom_logger/
│   │   ├── __init__.py
│   │   ├── authentication.py
│   │
│   ├── core/
│   │   ├── auth.py
│   │   ├── permissions.py
│   │   ├── user_services.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── user_routes.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── jwt_utils.py
│   │   ├── redis.py
│   │
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│
├── venv/
├── .env
├── env.example
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .gitignore             # Git ignore file
├── Readme.md              # Project documentation
└── requirements.txt       # Python dependencies
```