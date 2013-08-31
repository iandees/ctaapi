import requests
import xml.etree.ElementTree as ET
import datetime

class TrainTrackerException(Exception):
    pass

class Train(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'http://lapi.transitchicago.com/api/1.0'

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
    def _build_eta_dict(cls, eta):
        return {
            'station_id': eta.find('staId').text,
            'stop_id': eta.find('stpId').text,
            'station_name': eta.find('staNm').text,
            'stop_description': eta.find('stpDe').text,
            'route_name': eta.find('rt').text,
            'destination_stop_id': eta.find('destSt').text,
            'destination_name': eta.find('destNm').text,
            'direction': eta.find('trDr').text,
            'prediction_time': Train.parseTime(eta.find('prdt').text),
            'arrival_time': Train.parseTime(eta.find('arrT').text),
            'approaching': cls.parseBool(eta.find('isApp').text),
            'scheduled': cls.parseBool(eta.find('isSch').text),
            'fault': cls.parseBool(eta.find('isFlt').text),
            'delayed': cls.parseBool(eta.find('isDly').text),
            'lat': cls.parseFloat(eta.find('lat')),
            'lon': cls.parseFloat(eta.find('lon')),
            'heading': cls.parseFloat(eta.find('heading'))
        }

    def arrivals(self, map_id=None, stop_id=None, max_results=None, route_id=None):
        payload = {
            'mapid': map_id,
            'stpid': stop_id,
            'max': max_results,
            'rt': route_id,
            'key': self.api_key
        }
        resp = requests.get('%s/ttarrivals.aspx' % self.base_url, params=payload)
        resp.encoding = 'utf-8-sig'

        root = ET.fromstring(resp.text)

        if root.find('errCd').text != '0':
            raise TrainTrackerException(root.find('errNm').text)

        return [self._build_eta_dict(eta) for eta in root.iter('eta')]

    def follow_train(self, run_number):
        payload = {
            'runnumber': run_number,
            'key': self.api_key
        }
        resp = requests.get('%s/ttfollow.aspx' % self.base_url, params=payload)
        resp.encoding = 'utf-8-sig'

        root = ET.fromstring(resp.text)

        if root.find('errCd').text != '0':
            raise TrainTrackerException(root.find('errNm').text)

        position = root.find('position')

        return {
            'position': {
                'lat': self.parseFloat(position.find('lat')),
                'lon': self.parseFloat(position.find('lon')),
                'heading': self.parseFloat(position.find('heading'))
            },
            'stops': [self._build_eta_dict(eta) for eta in root.iter('eta')]
        }


if __name__ == '__main__':
    t = Train('c9436ba5fdc845db8981c144d76e2989')
    print t.arrivals(map_id=40380, route_id='Brn')
    print t.follow_train(609)