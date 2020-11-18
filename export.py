#!/usr/bin/env python

from lib.endomondo import Endomondo
import lib.tcx as tcx
import re
import getpass
import sys
import os, datetime


# create a somewhat useful filename for the specified workout
def create_filename(workout):
    ret = ''
    if workout.start_time:
        ret = workout.start_time.strftime("%Y%m%d") + "_"
    ret += str(workout.id)
    name = workout.name
    if name:
        name = re.sub(r'[\[\]/\\;,><&*:%=+@!#\(\)\|\?\^]', '', name)
        name = re.sub(r"[' \t]", '_', name)
        ret += "_" + name
    ret += ".tcx"
    return ret


# create a new directory to store the exported files in
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# create the TCX file for the specified workout
def create_tcx_file(workout, garmin):
    directory_name = 'export'
    activity = workout.get_activity()
    name = create_filename(workout)
    create_directory(directory_name)
    filename = os.path.join(directory_name, name)
    print "writing %s, %s, %s trackpoints" % (filename, activity.sport, len(activity.trackpoints))

    writer = tcx.Writer(garmin)
    tcxfile = writer.write(activity)
    if tcxfile:
        with open(filename, 'w') as f:
            f.write(tcxfile)


def main():
    try:
        print "Endomondo: export most recent n workouts (or ALL) as TCX files."
        mail = raw_input("Email: ")
        password = getpass.getpass()
        maximum_workouts = raw_input("Maximum number of workouts n (press Enter to ignore): ")
        garmin = raw_input("Format for Garmin Connect? (press Enter to ignore): ")
        endomondo = Endomondo(mail, password, garmin)
        if garmin:
            print "Files will be formatted to be compatible with Garmin Connects import function."

        if not maximum_workouts:
            days_per_year = 365.24
            maximum_workouts = 500
            print "Downloading workouts from the last 15 years in chunks. (If you logged more than 500 workouts per year, this won't work)"
            for years in range(0,20):
                before=(datetime.datetime.now()-datetime.timedelta(days=(days_per_year*years)))
                after=before-datetime.timedelta(days=(days_per_year*(1)))
                print "Chunk before:" +str(before)
                print "Chunk after:" +str(after)
                workouts = endomondo.get_workouts(maximum_workouts, before, after)
                for workout in workouts:
                    create_tcx_file(workout,garmin)
            print "done."
            return 0

        workouts = endomondo.get_workouts(maximum_workouts, before=None, after=None)
        print "fetched latest", len(workouts), "workouts"
        for workout in workouts:
            create_tcx_file(workout, garmin)
        print "done."
        return 0

    except ValueError, exception:
        sys.stderr.write(str(exception) + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
