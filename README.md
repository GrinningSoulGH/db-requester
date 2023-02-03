db-requester
============

Test project for a job application

## Build

To build, run from the project root:
```
$(venv) python setup.py sdist
```

## Installation

To install, run from the project root:
```
$(venv) pip install dist/db-requester-{VERSION}.tar.gz
```

## Running
To populate the database, run
```
$(venv) db_populate --path='${DB_PATH}'
```
Population script is repeatable, on subsequent runs adds rows to the `queue_requests` table.
Then, make sure to add DB_PATH to the service config file (template is in `config.yaml`).
To query the database, run
```
$(venv) db_query --path='${DB_PATH}'
```
To cleanup the database, run
```
$(venv) db_query --path='${DB_PATH}'
```
Make database and s2 credentials file (template is in `credentials.yaml`).
And run the service:
```
$(venv) db_requester -c "${DB_PATH}", --cred "${CREDENTIALS_PATH}"
```

## Tests
This package uses pytest for testing.
To install pytest run:
```
$(venv) pip install pytest
```
To start the tests run:
```
$(venv) pytest
```
