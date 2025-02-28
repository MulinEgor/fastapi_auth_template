# FastAPI Auth Teamplate

[![Static Badge](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org)
[![Static Badge](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Static Badge](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)](https://swagger.io)
[![Static Badge](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Static Badge](https://img.shields.io/badge/-SQLAlchemy-ffd54?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Static Badge](https://img.shields.io/badge/docker-257bd6?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)


## Установка и запуск проекта

1. Установить [uv](https://docs.astral.sh/uv/getting-started/installation/).

2. Клонировать проект:
```bash
git clone git@github.com:MulinEgor/fastapi_auth_template.git
```

3. Перейти в корневую директорию проекта.

4. Установить зависимости, включая зависимости для разработки:

```bash
uv sync --extra dev
```

5. Создать `.env` на основании `.env.example`:

```bash
cp -r src/.env.example src/.env`
```

6. Запустить API и PostgreSQL в Docker контейнерах:
```bash
make start_dev
```

7. Применить миграции:
```bash
make migrate
```

8. Документация API и доступные эндпоинт:
* Swagger UI: http://127.0.0.1:8000/docs
* ReDoc: http://127.0.0.1:8000/redoc

9. Для остановки контейнеров выполнить
```bash
make stop_dev
```

## Тесты
1. Перед запуском тестов необходимо создать `.env.test` на основе`.env.test.example`:
```bash
cp -r src/.env.test.example src/.env.test
```

2. Тесты запускаются из независимой базы данных Postgres с помощью команды `make test`.

    По умолчанию тесты запускаются в двух процессах `pytest` с двумя контейнерами PostgreSQL.

3. После выполнения тестов в файле `htmlcov/index.html` можно увидеть отчет о покрытии кода тестами.
