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
        return float(b) if b is not None else b

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
        print resp.url

        root = ET.fromstring(resp.text)

        if root.find('errCd').text != '0':
            raise TrainTrackerException(root.find('errNm').text)

        def build_eta_dict(eta):
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
                'approaching': self.parseBool(eta.find('isApp').text),
                'scheduled': self.parseBool(eta.find('isSch').text),
                'fault': self.parseBool(eta.find('isFlt').text),
                'delayed': self.parseBool(eta.find('isDly').text),
                'lat': self.parseFloat(eta.find('lat').text),
                'lon': self.parseFloat(eta.find('lon').text),
                'heading': self.parseFloat(eta.find('heading').text)
            }

        return [build_eta_dict(eta) for eta in root.iter('eta')]

if __name__ == '__main__':
    t = Train('c9436ba5fdc845db8981c144d76e2989')
    print t.arrivals(map_id=40380, route_id='Brn')