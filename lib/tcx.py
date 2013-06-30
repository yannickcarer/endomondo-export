import lxml.etree


class Trackpoint:
    def __init__(self):
        self.timestamp = None
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude_meters = 0.0
        self.distance_meters = 0.0
        self.sensor_state = "Absent"
        self.heart_rate = None
        self.cadence = None


class ActivityLap:
    def __init__(self):
        self.start_time = None
        self.timestamp = None
        self.total_time_seconds = 0.0
        self.distance_meters = 0.0
        self.maximum_speed = 0.0
        self.calories = 0
        self.intensity = "Active"
        self.trigger_method = "Distance"
        self.avg_heart = 0.0
        self.max_heart = 0.0
        self.avg_cadence = 0.0
        self.cadence = None


class Activity:
    def __init__(self):
        self.sport = "Running"
        self.start_time = ''
        self.notes = None
        self.laps = []
        self.trackpoints = []


class Writer:

    TCD_NAMESPACE = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    XML_SCHEMA_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"

    def create_element(self, parent, tag, text=None):
        tag = "{%s}%s" % (self.TCD_NAMESPACE, tag)

        nsmap = {
            None: self.TCD_NAMESPACE,
            "xsi": self.XML_SCHEMA_NAMESPACE,
        }
        element = lxml.etree.Element(tag, nsmap=nsmap)

        if text:
            element.text = text

        if parent is not None:
            parent.append(element)

        return element

    def time_to_s(self, t):
        return t.strftime("%Y-%m-%dT%H:%M:%SZ")

    def add_property(self, element, name, value):
        if value:
            if not isinstance(value, str):
                value = str(value)
            self.create_element(element, name, value)

    def add_trackpoint(self, element, v):
        elem = self.create_element(element, "Trackpoint")

        self.create_element(elem, "Time", self.time_to_s(v.timestamp))

        if v.latitude and v.longitude:
            pos = self.create_element(elem, "Position")
            self.add_property(pos, "LatitudeDegrees", v.latitude)
            self.add_property(pos, "LongitudeDegrees", v.longitude)

        self.add_property(elem, "AltitudeMeters", v.altitude_meters)
        self.add_property(elem, "DistanceMeters", v.distance_meters)
        self.add_heart_rate(elem, "HeartRateBpm", v.heart_rate)
        self.add_property(elem, "Cadence", v.cadence)

    def add_heart_rate(self, element, name, value):
        if value:
            elem = self.create_element(element, name)
            self.add_property(elem, "Value", int(value))

    def add_lap(self, element, activity, lap):
        elem = self.create_element(element, "Lap")
        elem.set("StartTime", self.time_to_s(lap.start_time))

        self.add_property(elem, "TotalTimeSeconds", lap.total_time_seconds)
        self.add_property(elem, "DistanceMeters", lap.distance_meters)
        self.add_property(elem, "MaximumSpeed", lap.maximum_speed)
        self.add_property(elem, "Calories", lap.calories)
        self.add_heart_rate(elem, "AverageHeartRateBpm", lap.avg_heart)
        self.add_heart_rate(elem, "MaximumHeartRateBpm", lap.max_heart)
        self.add_property(elem, "Intensity", lap.intensity)
        self.add_property(elem, "Cadence", lap.cadence)
        self.add_property(elem, "TriggerMethod", lap.trigger_method)

        # Add trackpoints
        for w in activity.trackpoints:
            self.add_trackpoint(elem, w)

    def add_activity(self, element, activity):
        sport = activity.sport
        if not sport:
            sport = "Other"

        elem = self.create_element(element, "Activity")
        elem.set("Sport", sport)
        self.create_element(elem, "Id", self.time_to_s(activity.start_time))
        self.create_element(elem, "Notes", activity.notes)

        for lap in activity.laps:
            self.add_lap(elem, activity, lap)

    def create_document(self, activity):
        document = self.create_element(None, "TrainingCenterDatabase")
        document.set("{%s}schemaLocation" % self.XML_SCHEMA_NAMESPACE, "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd")

        document = lxml.etree.ElementTree(document)
        element = self.create_element(document.getroot(), "Activities")
        self.add_activity(element, activity)
        return document

    def write(self, activity):
        self.laps = []
        self.trackpoints = []

        document = self.create_document(activity)
        return lxml.etree.tostring(document.getroot(),
                                   pretty_print=True,
                                   xml_declaration=True,
                                   encoding="UTF-8")
