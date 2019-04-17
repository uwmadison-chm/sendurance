# Sendurance

A centralized fitbit data-gathering tool to allow aggregating data from a 
fleet of fitbits, for scientific study purposes.

Instead of using `python-fitbit`, this connects directly with 
`requests-oauthlib`. It caches tokens in `tokens/` and attempts to make the refresh-token dance happen 
automatically.

## Requirements

    pip3 install requests requests_oauthlib

For development/console stuff, you'll want IPython:

    pip3 install ipython

## Getting started

Store your client id and secret somewhere secure (like in a `client.json` file, 
see `console.py` for an implementation)



Then you can just:

    from fitbit_api import FitbitApi
    fitbit = FitbitApi('email.address@wisc.edu', client_id, client_secret)

## Console mode

Create a `client.json` file that looks something like

    {"id": "77DFRL", "secret": "deadbeef001010101001111" }

Then run:

    python3 console.py email.address@wisc.edu

Now there's a "fitbit" object you can play with.

    fitbit.activities()
