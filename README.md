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

    from fitbit_api import FitbitApi
    fitbit = FitbitApi('email.address@wisc.edu')

## Console mode

    python3 console.py email.address@wisc.edu

Now there's a "fitbit" object you can play with.

    fitbit.activities()
