# mvtracking-backend-hub
Backend services for MV Tracking project

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://docs.python.org/3/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenAPI](https://img.shields.io/badge/openapi-6BA539?style=for-the-badge&logo=openapi-initiative&logoColor=fff)](https://www.openapis.org/)
[![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)](https://swagger.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://black.readthedocs.io/en/stable/)
[![Typed with: pydantic](https://img.shields.io/badge/typed%20with-pydantic-BA600F.svg?style=for-the-badge)](https://docs.pydantic.dev/)


## CI

[MV-Tracking-Backend-Pipeline](https://github.com/sagemicrosystems/mvtracking-backend-hub/actions)

- Creates a branch (eg. feature/clean-architecture) for each pull request from the `development` branch
- After PR reviews and approval, merge to `development` branch
- Creates PR to merge to `main` branch and deploys to staging

## Development

Requirements:
  - [docker](https://www.docker.com/)
  - [docker-compose](https://docs.docker.com/compose/)
  - [make](https://www.gnu.org/software/make/manual/html_node/Introduction.html)

Want to contribute? That is absolutely flip-flop awesome! Please make sure to inform mvitracking team
about the changes you'd like to make in the form of a pull-request before you do any merges to master.

### Setup

```bash
git clone https://github.com/sagemicrosystems/mvtracking-backend-hub.git

cd mvtracking-backend-hub

cp .env-example .env

make setup
```

### Run API
```bash

make run-api
```
### Run project on staging server
docker run -d --publish 8000:8000 --name mvi_hub_api --env-file .env  sagemicrosystems/mvi-hub:latest

## API

Available API [docs](http://localhost:8000/docs)

## References
1. [FastAPI official docs](https://fastapi.tiangolo.com/)
2. [alembic official tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
3. [Dependency Injector](https://python-dependency-injector.ets-labs.org/)
4. [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
