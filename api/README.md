## Instructions

- Make sure you have the INESCTEC VPN connection active in order to communicate
with the IOTA NODE.
- Run the **docker-compose** file in the root of the repository
- Get the Postman collection from the *Team Workspace*


### HORNET
1. https://hornet.docs.iota.org/welcome.html
2. https://github.com/demichele/install-hornet-1.5
3. https://github.com/svenger87/hornet-alphanet-tutorial
   #### Peering
4. https://hornet.docs.iota.org/post_installation/peering.html

#### Debug Service
- sudo systemctl restart hornet-testnet && sudo journalctl -u hornet-testnet -f

#### Auto-Peering

    "p2p": {
    ...
    "autopeering": {
      "entryNodes": [
        "/dns/lucamoser.ch/udp/14926/autopeering/9pTKhgpxnrf99Arw4EX1tgpfDPW1a4TuZPq6Sfk5Ku66",
        "/dns/iota-tangle.io/udp/14926/autopeering/FHFgAhJ25ZyMoQnsnoMRaU9KQJNVWMVqpnfmQBkhPBfZ"
      ],
      "bindAddress": "0.0.0.0:14626",
      "runAsEntryNode": false,
      "dirPath": "/tmp/p2pstore"
    }
}, 

### Cli Wallet
- https://github.com/iotaledger/cli-wallet

### Data Tables

CREATE TABLE raw_data
(
  username    varchar PRIMARY KEY,
  datetime    TIMESTAMP,
  ts          TIMESTAMP,
  value       FLOAT,
  unit        varchar,
  hash_tangle varchar
);

CREATE TABLE processed_data
(
  username varchar PRIMARY KEY,
  datetime TIMESTAMP,
  value    FLOAT,
);

CREATE TABLE forecast_data
(
  username varchar PRIMARY KEY,
  launch_time TIMESTAMP,
  market_session INT,
  value FLOAT,
  unit VARCHAR,
  hash_tangle VARCHAR
)

### Initialize market engine (for test purposes)

- Start by creating a superuser to the platform
  - inside the container run **python manage.py createsuperuser**
- Login the superuser (market user) ( POST `/api/token/login`)
- Create the market wallet ( GET `/api/wallet/create`)
- Create roles in the platform (Seller, Buyer, etc) ( POST `/api/user/role`)
- Register users with roles assigned
- Create market session ( POST `/api/market/session`)
- Place bids with each buyer 
  - First login with the user that needs to bid ( POST `/api/token/login`)
  - Only then, place bid (with user auth token) a different transaction id must be informed ( POST `/api/market/bid`)
- List session participants with bids
  * Login with superuser (to obtain priviledges to create new session)  ( POST `/api/token/login`)
  * Get list of session agents w/ bids ( GET `/api/market/bid?market_session_id=1`)

- List active sellers on the platform using the User Role by_role_id
  * Login with superuser (to obtain priviledges to create new session)  (`/api/token/login`)
  * Get list of session seller agents ( GET `/api/user/role-by-user/?role_id=2`)
  
- Distribute payouts to wallet withdraw ( POST `/api/wallet/withdraw`) 
- Get list of payouts pending ( GET `/api/wallet/withdraw`)

Notes:

The objective of this test is to assure simple tasks as of create/close market sessions and schedule payouts
are correctly set.

In these tests the bids doesn't include the functionality of actually moving IOTA. It should be the desktop app to 
deliver that before posting the Bid.


### Instructions to clear the Database

- Remove the file **db.sqlite3** from the api folder
- Remove all migrations from the different apps (user, wallet, market)
- Run again the docker-compose
- Run the following commands in the container:   
    - python manage.py makemigrations 
    - python manage.py migrate
    - python manage.py createsuperuser
    
## RESTful API Source Code

- https://hornet.docs.iota.org/post_installation/config.html
- https://github.com/svenger87/hornet-alphanet-tutorial

## Faucet
- https://faucet.testnet.chrysalis2.com/
- https://faucet.tanglekit.de/

### Faucet Development
- https://github.com/iotaledger/chrysalis-faucet

## Other stuff
- Queries: https://docs.djangoproject.com/en/3.2/topics/db/queries/
- IOTA stackexchange: https://iota.stackexchange.com/
- IOTA wallet documentation: https://wallet-lib.docs.iota.org/libraries/python/examples.html

## Tests

### Superuser 
1. Superuser can't create a new market session if there is other session with a status different than finished.
2. Superuser can't bid on any session
3. Only Superuser can create market sessions and change their data, status, etc.
4. 

## Hornet tutorial
1. https://github.com/svenger87/hornet-alphanet-tutorial
2. https://github.com/demichele/install-hornet-1.5

## Gunicorn
- https://stackoverflow.com/questions/10855197/gunicorn-worker-timeout-error

## Exception codes

1. Email already exists: 409
2. Duplicated bid: 409


## CLI-Wallet
- git clone https://github.com/iotaledger/cli-wallet.git
- cargo build

## Research Specifications
- https://github.com/iotaledger/IOTA-2.0-Research-Specifications

# Errors
- Check balance or checking address
  This error occurs every
  1. thread 'pool-thread-#7' panicked at 'called `Result::unwrap()` on an `Err` value: ReturnControlRequest(SLIP10Derive(Ok([209, 30, 97, 243, 45, 94, 101, 154, 71, 244, 78, 230, 22, 109, 175, 94, 102, 5, 67, 9, 209, 7, 134, 199, 145, 121, 108, 76, 148, 199, 176, 97])))', /root/.cargo/registry/src/github.com-1ecc6299db9ec823/stronghold-utils-0.3.0/src/ask.rs:48:42
