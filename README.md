# Sendurance

A centralized fitbit data-gathering tool to allow aggregating data
from a fleet of fitbits, for scientific study purposes.

Instead of using `python-fitbit`, this just connects straight with 
`requests-oauthlib`.

## Requirements

    pip3 install requests requests_oauthlib

For development/console stuff, you'll want IPython:

    pip3 install ipython

## Getting Started

    python3 console.py email.address@wisc.edu

Now there's a "fitbit" object you can play with.

    fitbit.activities()
