import requests
import xml.etree.ElementTree as ET
import datetime

class BusTrackerException(Exception):
    pass

class BusTracker(object):
    """ http://www.transitchicago.com/assets/1/developer_center/BusTime_Developer_API_Guide.pdf """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'http://www.ctabustracker.com/bustime/api/v1'

    @classmethod
    def parseTime(cls, ts):
        return datetime.datetime.strptime(ts, '%Y%m%d %H:%M:%S')
    @classmethod
    def parseBool(cls, b):
        if b == '1':
            return True
        elif b == '0':
            return False
    @classmethod
    def parseFloat(cls, b):
        return float(b.text) if b is not None else b
    @classmethod
    def parseInt(cls, b):
        return int(b.text) if b is not None else b

    def get_time(self):
        payload = {
            'key': self.api_key
        }
        resp = requests.get('%s/gettime' % self.base_url, params=payload)
        resp.encoding = 'utf-8-sig'

        root = ET.fromstring(resp.text)

        if root.find('error') is not None:
            raise BusTrackerException(root.find('error').find('msg').text)

        return self.parseTime(root.find('tm').text)

    def get_vehicles(self, vehicle_ids=None, route_ids=None):
        payload = {
            'key': self.api_key,
            'vid': ','.join(vehicle_ids) if vehicle_ids else None,
            'rt': ','.join(route_ids) if route_ids else None
        }
        resp = requests.get('%s/getvehicles' % self.base_url, params=payload)
        resp.encoding = 'utf-8-sig'

        root = ET.fromstring(resp.text)

        if root.find('error') is not None:
            raise BusTrackerException(root.find('error').find('msg').text)

        def parseVehicle(v):
            return {
                'vehicle_id': v.find('vid').text,
                'timestamp': self.parseTime(v.find('tmstamp')),
                'lat': self.parseFloat(v.find('lat')),
                'lon': self.parseFloat(v.find('lon')),
                'heading': self.parseInt(v.find('hdg')),
                'pattern_id': self.parseInt(v.find('pid')),
                'pattern_distance': self.parseInt(v.find('pdist')),
                'route_id': v.find('rt').text,
                'destination': v.find('des').text,
                'delayed': self.parseBool(v.find('dly'))
            }

        return [parseVehicle(v) for v in root.iter('vehicle')]

    def get_predictions(self, stop_ids=None, route_ids=None, vehicle_ids=None, max_results=None):
        payload = {
            'key': self.api_key,
            'stpid': ','.join(stop_ids) if stop_ids else None,
            'rt': ','.join(route_ids) if route_ids else None,
            'vid': ','.join(vehicle_ids) if vehicle_ids else None,
            'top': max_results
        }
        resp = requests.get('%s/getpredictions' % self.base_url, params=payload)
        resp.encoding = 'utf-8-sig'

        root = ET.fromstring(resp.text)

        if root.find('error') is not None:
            raise BusTrackerException(root.find('error').find('msg').text)

        def parsePrediction(v):
            return {
                'timestamp': self.parseTime(v.find('tmstamp')),
                'type': v.find('typ').text,
                'stop_id': self.parseInt(v.find('stpid')),
                'stop_name': v.find('stpnm').text,
                'vehicle_id': v.find('vid').text,
                'distance_remaining': self.ParseInt(v.find('dstp')),
                'route_id': v.find('rt').text,
                'route_directon': v.find('rtdir').text,
                'destination': v.find('des').text,
                'arrival_time': self.parseTime(v.find('prdtm')),
                'delayed': self.parseBool(v.find('dly'))
            }

        return [parsePrediction(v) for v in root.iter('prd')]

if __name__ == '__main__':
    t = BusTracker('foo')
    print t.get_time()