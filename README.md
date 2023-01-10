### Requirements:
* [Docker](https://www.docker.com/)
* [Docker-compose](https://docs.docker.com/compose/)
* [Just](https://github.com/casey/just)

### Usage:
The easiest way of running this is using just.
* `just run` - Just runs the crawler and api.

Otherwise you can just spin up the crawler, postgres DB and api, however you will have to manually craft the env vars for the services to run correctly:
* `POSTGRES_DB=blah POSTGRES_PASSWORD=blah POSTGRES_USER=blah DB_HOST=db DB_CONN="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$DB_HOST:5432/$POSTGRES_DB" docker-compose up`

Once the crawler has populated the DB, you can access the api with:
* `curl -L 0.0.0.0:8000/`

### Dotenv
You will need to put the Postgres connection info in a dotenv file for just to pick up and export to the commands it runs.
The env vars that need to go in the .env file:
* POSTGRES_DB
* POSTGRES_PASSWORD
* POSTGRES_USER

### Development:
* `just debug` - Runs the crawler and API, and will output debug logs.
* `just update_reqs` - Update the poetry lockfile if you change the requirements.
* `just test` - Runs the test suite
* `just _remove_postgres_db` - Delete the contents of the DB (including the table).

## Big thanks to the Opensage project, and the excellent write-up by Tim Jones [here](https://opensage.github.io/blog/replay-file-parsing).
## Also thanks to the cnc-replayreaders project found [here](https://github.com/louisdx/cnc-replayreaders)
## Also thanks to Bill Rich who had found lots of the command codes [here](https://github.com/bill-rich/cncstats/blob/main/pkg/zhreplay/body/body.go)