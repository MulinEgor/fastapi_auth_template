# FastAPI Auth Template

[![Static Badge](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org)
[![Static Badge](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Static Badge](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)](https://swagger.io)
[![Static Badge](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Static Badge](https://img.shields.io/badge/-SQLAlchemy-ffd54?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Static Badge](https://img.shields.io/badge/docker-257bd6?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)


## Project Setup and Launch

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).

2. Install dependencies, including dev ones:

```bash
uv sync --extra dev
```

3. Create `.env` based on `.env.example`:

```bash
cp -r src/.env.example src/.env`
```

6. Start API and PostgreSQL in Docker containers:
```bash
make start_dev
```

7. Apply migrations:
```bash
make migrate
```

8. Docs:
* Swagger UI: http://127.0.0.1:8000/docs
* ReDoc: http://127.0.0.1:8000/redoc

9. Stoppage
```bash
make stop_dev
```

## Tests
1. Before starting tests, you need to create `.env.test` based on`.env.test.example`:
```bash
cp -r src/.env.test.example src/.env.test
```

2. By default, tests run on 2 PostgreSQL containers.

3. After running tests, in `htmlcov/index.html` you can see test coverage.
