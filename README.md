# Sendurance

A centralized fitbit data-gathering tool to allow aggregating data from a 
fleet of fitbits, for scientific study purposes.

Instead of using `python-fitbit`, this connects directly with 
`requests-oauthlib`. It caches tokens in `./tokens/` and attempts to make the 
refresh-token dance happen automatically using `geckodriver`.

## Requirements

    python3 -m virtualenv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt

Install a recent Firefox and put [geckodriver](https://github.com/mozilla/geckodriver/releases/) somewhere in your path, or put it in the sendurance directory.

## Mass downloading

### Using the Fleet Downloader

Create a `client.json` containing your Fitbit API id, secret, and the shared password on your fitbit accounts:

    {"id": "XYZ", "secret": "something", "password": "shared"}

Create a csv file with columns ID, Email log-in, First Day, and Last Day. Include rows for every Fitbit.

Then create a work event Excel file. TODO: Document as used by MP2 study.

Create an `input.json` file for each fleet, to link these two things:

    {
        "fleet_file": "/path/to/fleet_data.csv",
        "work_event_file": "/path/to/work_events.xlsx",
        "output_path": "/path/to/output"
    }

You can edit `fleet_downloader.py` to download the data you want. Change the 
lines at the bottom:
    
    Downloader.save_steps()
    Downloader.save_hrv()
    Downloader.save_sleep()

Then do

    python3 fleet_downloader.py input.json

### Other download styles

See [`afchron_downloader`](afchron_downloader.py) for an example of a 
study-specific downloader that works from a single wacky excel tracking file.

Run with -v or -vv for more details, including screenshots of geckobrowser 
during the login dance.

You will need a client.json with `id` (your client ID) and `secret` for the 
Fitbit API, and also a `password` field with what to use to log into the 
fitbits.

You can add custom per-fitbit passwords for accounts that did not get the main 
password in client.json in a hash `password-overrides`.

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

    python3 console.py email.address@wisc.edu password

Now there's a "fitbit" object you can play with.

    fitbit.activities()
    fitbit.get(...)
    
