db-requester
============

Test project for a job application.

## Dependencies
Python ~= 3.11

## Environment

To set up environment, run:
```
$(venv) pip install -r requirements.txt
```
## Configuration
Service is configured via a `.yaml` file (template is in config.yaml) and environment variables:
- DB_URL - [sqlalchemy-formatted url](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls);
- S2_LOGIN - login for the S2 service;
- S2_PASSWORD - password for the S2 service.

Database scripts use the environment variable DB_URL that is the same as service's.

Usage of any dialect and driver outside of sqlite with sqlite3 may require installing additional dependencies.

## Running
To populate the database, run
```
$(venv) env DB_URL="${DB_URL}" python populate_db.py
```
Population script is repeatable, on subsequent runs it adds rows to the `queue_requests` table.

To query the database, run
```
$(venv) env DB_URL="${DB_URL}" python query_db.py
```

To cleanup the database, run
```
$(venv) env DB_URL="${DB_URL}" python cleanup_db.py
```

To run S2:
```
$(venv) pip install aiohttp
$(venv) python -m aiohttp.web -H "${HOST}" -P "${PORT}" s2:init_func
```
where HOST and PORT are the host and port for S2 to bind to.

To run the service:
```
$(venv) env DB_URL="${DB_URL}" S2_LOGIN="{S2_LOGIN}" S2_PASSWORD="{S2_PASSWORD}" python main.py --config "${CONFIG_PATH}"
```
