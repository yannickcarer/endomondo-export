Endomondo Export
================

Export a user's most recent Endomondo workouts as TCX files.


Usage
-----

The script export.py may be used to backup the complete workout history:

    python export.py

You will be asked for your Endomondo email and password, and then the script will do the rest.


Requirements
------------

- Python 2.6+
    - lxml
    - requests


Installing
----------

To set up the requirements for this project, you can install the dependencies by pip.  

First, it's highly recommended to set up a virtualenv:

    virtualenv venv --distribute
    source ./venv/bin/activate

Then install the requirements:

    pip install -r requirements

And you're set!


Authors
-------

This script was created [@yannickcarer](https://github.com/yannickcarer), with some updates by [@mikedory](https://github.com/mikedory).
