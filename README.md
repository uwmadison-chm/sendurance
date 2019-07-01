# Sendurance

A centralized fitbit data-gathering tool to allow aggregating data from a 
fleet of fitbits, for scientific study purposes.

Instead of using `python-fitbit`, this connects directly with 
`requests-oauthlib`. It caches tokens in `./tokens/` and attempts to make the 
refresh-token dance happen automatically.

## Requirements

    python3 -m virtualenv .venv
    source .venv/bin/activate
    pip3 install requests requests_oauthlib

## Using the downloader

Create a csv file where column 1 is the ID and column 2 is the
email address of the fitbit account for that participant.

Then do

    python3 downloader.py accounts.csv --start-date=2019-03-01 --end-date=2019-04-01

or

    python3 downloader.py --help

## Developer details

For development/console stuff, you'll want IPython:

    pip3 install ipython

### Getting started with code

Store your client id and secret somewhere secure (like in a `client.json` file, 
see `console.py` for an implementation)

Then you can just:

    from fitbit_api import FitbitApi
    fitbit = FitbitApi('email.address@wisc.edu', client_id, client_secret)

### Console mode

Create a `client.json` file that looks something like

    {"id": "77DFRL", "secret": "deadbeef001010101001111" }

Then run a console with a fitbit account:

    python3 console.py email.address@wisc.edu

Now there's a "fitbit" object you can play with.

    fitbit.activities()
    fitbit.get(...)
    
## Using the Fleet Downloader

Create a csv file with columns ID, Email log-in, First Day, and Last Day. Include rows for every Fitbit. Either call this file `fleet_data.csv` or edit the fleet_file variable in `fleet_downloader.py` to point to this csv file.

You can edit `fleet_downloader.py` to download the data you want using the lines
    
    Downloader.save_steps()
    Downloader.save_hrv()
    Downloader.save_sleep()

Then do

    python3 fleet_downloader.py
