# Endomondo Export

This is an extended fork of https://github.com/yannickcarer/endomondo-export. Since Endomondo is shutting down it's service with the end of 2020 (what a year), i was searching for a way to export all my workouts (>1000) to Garmin Connect. yannickcarers script works fine, but you can not export more than ~500 workouts since the server will timeout roughly around 500 exports. I added a feature that downloads the last 20 years as chunks of 500 trainings and also added the option to format the output for Garmin Connect, which needs an extra <Track> Wrapper around trackpoints and only allows "Running", "Biking" and "Other" as activity names.

## Usage

The script export.py may be used to backup the complete workout history. You will be asked for your Endomondo email and password, followed by the number of workouts you want to export (leave empty to export the last 20 years) and if you want to format the export to be compatible with Garmin Connect.

**Important: If you have done more than 500 workouts in a year (congratulations!) you will run into problems using my script!**

```shell
python export.py
Endomondo: Export the most recent n workouts (or ALL) as TCX files.
Email: mymail@yourdomain.com
Password: 
Maximum number of workouts n (press Enter download ALL OF THEM): 5
Format for Garmin Connect? (press Enter to ignore): Y
Files will be formatted to be compatible with Garmin Connects import function.
fetched latest 5 workouts
writing export/20201113_1648626623.tcx, Other, 1 trackpoints
writing export/20201112_1647888548.tcx, Biking, 693 trackpoints
writing export/20201110_1647453368.tcx, Running, 1319 trackpoints
...
```

## Requirements


- Python 2.6+
    - lxml
    - requests


## Installing

```shell
pip install -r requirements
```

## Credit

This script was created [@yannickcarer](https://github.com/yannickcarer), with some updates by [@mikedory](https://github.com/mikedory) and some minor improvements of [@countablyinfinite](https://github.com/countablyinfinite)
