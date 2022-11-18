set dotenv-load
# Hardcode the db instance here as unless we put it in the dotenv file we can't access it in an export
export DB_CONN := `echo postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres_db_instance:5432/$POSTGRES_DB`
export DEBUG := ""

# Needed if the pyproject toml is updated. This updates the lock file.
update_reqs:
	cd api && poetry update
	cd crawler && poetry update

# Run the crawler and API
run *args:
     docker-compose up {{args}}

# Run with DEBUG enabled.
debug *args:
	DEBUG=True just run {{args}}

# Force build the docker compose containers.
force_run:
	just run --force-recreate --build --no-deps

# Build all the docker images.
docker_build:
	cd api && docker build . -t zh_api:latest
	cd crawler && docker build . -t zh_crawler:latest

# Remove the postgres db
_remove_postgres_db:
	docker-compose down --volumes

# Run the tests
test: docker_build
	#!/usr/bin/env bash
	set -euxo pipefail

	# Remove existing DB
	just _remove_postgres_db

	# Create a new postgres DB
	docker-compose up -d db

	# Let the DB start up
	sleep 2

	# Create the DB table
	docker run -e DB_CONN=$DB_CONN --add-host=host.docker.internal:host-gateway zh_crawler:latest "poetry run alembic upgrade head"

	# Run the tests
	docker run --add-host=host.docker.internal:host-gateway zh_crawler:latest "poetry run pytest"

	# Shutdown the postgres DB.
	docker-compose down