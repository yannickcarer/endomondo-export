#!/usr/bin/env python

from lib.endomondo import Endomondo
import lib.tcx as tcx
import re
import getpass
import sys
import os


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
def create_tcx_file(workout):
    directory_name = 'export'
    activity = workout.get_activity()
    name = create_filename(workout)
    create_directory(directory_name)
    filename = os.path.join(directory_name, name)
    print "writing %s, %s, %s trackpoints" % (filename, activity.sport, len(activity.trackpoints))

    writer = tcx.Writer()
    tcxfile = writer.write(activity)
    if tcxfile:
        with open(filename, 'w') as f:
            f.write(tcxfile)


def main():
    try:
        print "Endomondo: export most recent workouts as TCX files"

        email = raw_input("Email: ")
        password = getpass.getpass()
        maximum_workouts = raw_input("Maximum number of workouts (press Enter to ignore)")
        endomondo = Endomondo(email, password)

        workouts = endomondo.get_workouts(maximum_workouts)
        print "fetched latest", len(workouts), "workouts"
        for workout in workouts:
            create_tcx_file(workout)
        print "done."
        return 0

    except ValueError, exception:
        sys.stderr.write(str(exception) + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
