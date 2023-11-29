# mvtracking-backend-hub
Backend services for MV Tracking project

### CI

[MV-Tracking-Backend-Pipeline](https://github.com/sagemicrosystems/mvtracking-backend-hub/actions)

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

make setup && make run-api
```

## API

Available API [docs](http://localhost:8000/docs)
