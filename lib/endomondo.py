#!/usr/bin/env python

import tcx
import requests
import uuid
import socket
import datetime
import pytz
import sys

def to_datetime(v):
    return datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S %Z")


def to_float(v):
    if v == '' or v is None:
        return None
    return float(v)


def to_int(v):
    if v == '' or v is None:
        return None
    return float(v)


def to_meters(v):
    v = to_float(v)
    if v:
        v *= 1000
    return v

SPORTS_GARMIN = {
    0:  'Running',
    1:  'Biking',
    2:  'Biking',
    3:  'Biking',
    4:  'Other',
    5:  'Other',
    6:  'Other',
    7:  'Other',
    8:  'Other',
    9:  'Other',
    10: 'Other',
    11: 'Other',
    12: 'Other',
    13: 'Other',
    14: 'Other',
    15: 'Other',
    17: 'Other',
    18: 'Other',
    19: 'Other',
    20: 'Other',
    21: 'Other',
    22: 'Other',
    23: 'Other',
    24: 'Other',
    25: 'Other',
    26: 'Other',
    27: 'Other',
    28: 'Other',
    29: 'Other',
    30: 'Other',
    31: 'Other',
    32: 'Other',
    33: 'Other',
    34: 'Other',
    35: 'Other',
    36: 'Other',
    37: 'Other',
    38: 'Other',
    39: 'Other',
    40: 'Other',
    41: 'Other',
    42: 'Other',
    43: 'Other',
    44: 'Other',
    45: 'Other',
    46: 'Other',
    47: 'Other',
    48: 'Other',
    49: 'Other',
    50: 'Other'
}

SPORTS = {
    0:  'Running',
    1:  'Cycling, transport',
    2:  'Cycling, sport',
    3:  'Mountain biking',
    4:  'Skating',
    5:  'Roller skiing',
    6:  'Skiing, cross country',
    7:  'Skiing, downhill',
    8:  'Snowboarding',
    9:  'Kayaking',
    10: 'Kite surfing',
    11: 'Rowing',
    12: 'Sailing',
    13: 'Windsurfing',
    14: 'Fitness walking',
    15: 'Golfing',
    16: 'Hiking',
    17: 'Orienteering',
    18: 'Walking',
    19: 'Riding',
    20: 'Swimming',
    21: 'Spinning',
    22: 'Other',
    23: 'Aerobics',
    24: 'Badminton',
    25: 'Baseball',
    26: 'Basketball',
    27: 'Boxing',
    28: 'Climbing stairs',
    29: 'Cricket',
    30: 'Cross training',
    31: 'Dancing',
    32: 'Fencing',
    33: 'Football, American',
    34: 'Football, rugby',
    35: 'Football, soccer',
    36: 'Handball',
    37: 'Hockey',
    38: 'Pilates',
    39: 'Polo',
    40: 'Scuba diving',
    41: 'Squash',
    42: 'Table tennis',
    43: 'Tennis',
    44: 'Volleyball, beach',
    45: 'Volleyball, indoor',
    46: 'Weight training',
    47: 'Yoga',
    48: 'Martial arts',
    49: 'Gymnastics',
    50: 'Step counter'
}


class Endomondo:
    os = "Android"
    os_version = "2.2"
    model = "M"

    def __init__(self, email=None, password=None, garmin=None):
        self.auth_token = None
        self.request = requests.session()
        self.request.headers['User-Agent'] = self.get_user_agent()
        if email and password:
            self.auth_token = self.request_auth_token(email, password)
        self.garmin = garmin

    def get_user_agent(self):
        """HTTP User-Agent"""
        return "Dalvik/1.4.0 (Linux; U; %s %s; %s Build/GRI54)" % (self.os, self.os_version, self.model)

    def get_device_id(self):
        return "ebb1083f-7ead-5e11-9847-86fc1d77348e"#str(uuid.uuid5(uuid.NAMESPACE_DNS, socket.gethostname()))

    def request_auth_token(self, email, password):

        # API request for authentication
        params = {
            'email':            email,
            'password':         password,
            'country':          'US',
            'deviceId':         self.get_device_id(),
            'os':               self.os,
            'appVersion':       "7.1",
            'appVariant':       "M-Pro",
            'osVersion':        self.os_version,
            'model':            self.model,
            'v':                2.4,
            'action':           'PAIR'
        }
        r = self.request.get('http://api.mobile.endomondo.com/mobile/auth',
                             params=params)
        lines = r.text.split("\n")

        # check success
        if lines[0] != "OK":
            raise ValueError("Endomondo authentication failed, %s" % lines[0])

        # retrieve auth token
        for line in lines[1:]:
            key, value = line.split("=")
            if key == "authToken":
                return value

        return None

    def parse_text(self, response):
        """Parse API response as text"""
        lines = response.text.split("\n")
        if (len(lines) < 1):
            raise ValueError("Error: URL %s: empty response" % response.url)

        if lines[0] != "OK":
            raise ValueError("Error: URL %s: %s" % (response.url, lines[0]))
        return lines[1:]

    def parse_json(self, response):
        """Parse API response as JSON"""
        return response.json()['data']

    def call(self, url, format, params={}):
        """Call the Endomondo API"""

        # API request
        params.update({
            'authToken': self.auth_token,
            'language': 'EN'
        })
        r = self.request.get('http://api.mobile.endomondo.com/mobile/' + url,
                             params=params)

        # check success
        if r.status_code != requests.codes.ok:
            print "Error: failed GET URL %s" % r.url
            r.raise_for_status()
            return None

        # parse response in the appropriate format
        if format == 'text':
            return self.parse_text(r)
        if format == 'json':
            return self.parse_json(r)
        return r

    def get_workouts(self, max_results, before, after):
        """Get workouts""" 
        params = {'maxResults': max_results}
        if before:
            params.update({'after': self.to_endomondo_time(after)})
            params.update({'before': self.to_endomondo_time(before)})

        json = self.call('api/workout/list', 'json', params)
        return [EndomondoWorkout(self, w, self.garmin) for w in json]

    def to_endomondo_time(self,time):
        return time.strftime("%Y-%m-%d %H:%M:%S UTC")


    def to_python_time(self, endomondo_time):
        return datetime.datetime.strptime(endomondo_time, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=pytz.utc)


class EndomondoWorkout:
    """Endomondo Workout wrapper"""

    def __init__(self, parent, properties, garmin):
        self.parent = parent
        self.properties = properties
        self.activity = None
        self.garmin = garmin

    # dict wrapper
    def __getattr__(self, name):
        value = None
        if name in self.properties:
            value = self.properties[name]
            if name == 'sport':
                if self.garmin:
                    value = SPORTS_GARMIN.get(value, 'Other')
                else:
                    value = SPORTS.get(value, 'Other')
            elif name == 'start_time':
                value = to_datetime(value)
        return value

    def get_activity(self):
        """The TCX activity equivalent to this workout"""

        if self.activity:
            return self.activity

        # call to retrieve activity data
        lines = self.parent.call('readTrack', 'text', {'trackId': self.id})

        # the 1st line is activity details
        data = lines[0].split(";")
        try:
            start_time = to_datetime(data[6])
        except Exception as e:
            print "start time"
            sys.exit()
        self.activity = tcx.Activity()
        if self.garmin:
            self.activity.sport = SPORTS_GARMIN.get(int(data[5]), "Other")
        else:
            self.activity.sport = SPORTS.get(int(data[5]), "Other")
        self.activity.start_time = start_time
        self.activity.notes = self.notes

        # create a single lap for the whole activity
        l = tcx.ActivityLap()
        l.start_time = start_time
        l.timestamp = start_time
        l.total_time_seconds = to_float(data[7])
        l.distance_meters = to_meters(data[8])
        l.calories = to_int(data[9])
        l.min_altitude = to_float(data[11])
        l.max_altitude = to_float(data[12])
        l.max_heart = to_float(data[13])
        l.avg_heart = to_float(data[14])
        self.activity.laps.append(l)

        # extra lines are activity trackpoints
        for line in lines[1:]:
            data = line.split(";")
            if len(data) >= 9:
                w = tcx.Trackpoint()    
                try:
                    w.timestamp = to_datetime(data[0])
                except Exception as e:
                    w.timestamp=start_time
                w.latitude = to_float(data[2])
                w.longitude = to_float(data[3])
                w.altitude_meters = to_float(data[6])
                w.distance_meters = to_meters(data[4])
                w.heart_rate = to_int(data[7])
                self.activity.trackpoints.append(w)

        return self.activity
