# Data Sharing Barter Incentives - RESTful API + Database

-----------------------------------------------------

[![version](https://img.shields.io/badge/version-0.0.1-blue.svg)]()
[![status](https://img.shields.io/badge/status-development-yellow.svg)]()
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-360/)

## Requirements

* [Python 3.10+](https://www.python.org/downloads/)
* [Pip ^21.x](https://pypi.org/project/pip/)


## Project Structure:

The following directory structure should be considered:

``` bash
.   # Current directory
├── api   # REST API source code
├──── api
├──── authentication          # authentication endpoints
├──── data                    # data operations endpoints
|──── logs                    # logs directory
├──── market                  # market participation endpoints
├──── tests                   # unittests suite
├──── users                   # users endpoints
├── nginx                     # NGINX configs
├── docs                      # Docs
├── .dockerignore             # gitignore file
├── .gitignore                # gitignore file
├── .gitlab-ci.yml            # gitlab-ci file
├── docker-compose.prod.yml   # docker-compose file (production)
├── docker-compose.test.yml   # docker-compose file (CICD)
├── docker-compose.yml        # docker-compose file (development)
├── README.md
```

## Project Setup

Create a `.env` file from a provided example (`dotenv`) and update its variables
```shell
cp dotenv .env
```

Start docker stack:

```shell
docker-compose up -d
```

Enter docker container (app):

```shell
docker exec -it predico_rest_app bash
```

Inside the container (`predico_rest_app`) apply current migrations and create superuser.

```shell
python manage.py migrate
python manage.py createsuperuser
```

Run collectstatic to serve static files
```shell
python manage.py collectstatic
```


Check if all tests pass successfully

```shell
pytest
```

See the Swagger (http://0.0.0.0:80/swagger) for methods description.


## How to easy deploy in "debug" mode (developers)?

How to run the code in development mode, with APP decoupled from docker stack?

First, install the necessary project python dependencies:


```shell
cd /api
pip install -r requirements.txt
```

Then, create a `.dev.env` file with environment variables used to debug and update default environment variables to your specifics.

**Important:** Make sure you force develop mode by using the following environment variable `DJANGO_APPLICATION_ENVIRONMENT=develop` and `POSTGRES_HOST=localhost`


Then, use docker-compose to initialize a Postgres DB:

```shell
docker-compose up -d --build postgresql
```

Once your DB is up, you can debug locally by just by uncommenting the following lines in "environment.lines: 

```python
from dotenv import load_dotenv
load_dotenv(".dev.env")
```

After this, you can easily run your application without docker container, in either an IDE or straight from the command line.

1. Migrate your DB migrations:

```shell
python manage.py migrate
```

2. Create a superuser:

```shell
python manage.py createsuperuser
```

3. Run your app using through Django runserver command:

```shell
python manage.py runserver
```


## Example of a Market Configuration Pipeline:

**Important: This is only for administrators**
1. Login with superuser (market admin) ( POST `/api/token`)
2. Register a market wallet address ( POST `/api/market/wallet-address`)
   * Note1: this market address will be used by external users to make crypto transfers during bid placement phase
   * Note2: this address can be updated via REST too ( PUT `/api/market/wallet-address`)

## Example of a Market Session Pipeline:
1. Login with superuser (market admin) ( POST `/api/token`)
2. Create a new market session ( POST `/api/market/session`):
   * Note: Once created, market sessions are set to a "staged" status.
3. Update market session status to 'open' to unlock bid placement phase ( PATCH `/api/market/session/<market_session_id>`)
   * Important: Bids can only be placed once session is on `open` status
4. Users can now place their bids. Market Engine (`predico-market` repository) will validate each bids and update its status via ( POST `/api/market/validate/bid-payment`)
5. Once gate closure time is reached (scheduled time) - Market admin changes market session status to 'running' ( PATCH `/api/market/session/<market_session_id>`) 
6. Market Runs & new session is staged automatically (which will be opened in a scheduled bases later on, for bid acceptance)

## Example of a User Configuration Pipeline:
1. Register (POST `/api/user/register`) - save `verificatio_link`
   1.1. Validate user (perform GET request to `verification_link` url to validate user)
2. Login ( POST `/api/token` )
3. Register wallet address (used as reference for token transfers from market to user)
   * Note: this address can be updated via REST too ( PUT `/api/user/wallet-address`)
4. Register a user resource (e.g. a wind farm under user portfolio) ( POST `/api/user/resource`)
   * Note: this resource can be updated via REST too ( PATCH `/api/user/resource/<resource_id>`)

## Example of a User Market Participation Pipeline:
1. Users can send measurements data to the market ( POST `/api/data/raw-data`)
   * This data can also be accessed via REST ( GET `/api/data/raw-data`)
   * Note: Users should continuously send measurements for their resources to maximize their participation in the market (seller role is obligatory for all users)

2. Once a market session is on 'open' status, users can place their bids. A bid pipeline should be the following:
   * See market session details ( GET `/api/market/session`) and search for last open session
   * Get market wallet address ( GET `/api/market/wallet-address`)
   * Make crypto transfer to market wallet address and save transfer message identifier (e.g., DLT transaction identifier)
   * Post bid details ( POST `/api/market/bid/`)
   * Associate a IOTA tangle message identifier to a specific bid ID in url para ( PATCH `/api/market/bid/:bid_id`)

3. Users can check their bids & bid status (if is confirmed or not by market engine) ( GET `/api/market/bid/`)

4. At each market run, forecasts will be produced for resources with bids. These forecasts are accessible via REST (GET `/api/data/market-forecasts`)


## Contacts:

If you have any questions regarding this project, please contact the following people:

Developers (SW source code / methodology questions):
  - José Andrade <jose.r.andrade@inesctec.pt>
  - André Garcia <andre.f.garcia@inesctec.pt>

Contributors / Reviewers (methodology questions):
  - Carla Gonçalves <carla.s.goncalves@inesctec.pt>
  - Ricardo Bessa <ricardo.j.bessa@inesctec.pt>
