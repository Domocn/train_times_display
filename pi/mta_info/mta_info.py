import requests, time
from google.protobuf.message import DecodeError

from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict

MTA_URL = 'http://datamine.mta.info/mta_esi.php'
TIMES_TO_GET = 6


class MTAInfo:
    def __init__(self, api_key, feed_id, station):
        self.api_key = api_key
        self.feed_id = feed_id
        self.station = station
        self.feed_message = gtfs_realtime_pb2.FeedMessage()
        
    @staticmethod
    def get_train_time_with_label(train, arrival_time, now):
        minutes_until_train = (arrival_time - int(now)) // 60
        minutes = "{}".format(minutes_until_train)
        return "{}: {}".format(train, minutes)

    @staticmethod
    def get_train_time(arrival_time, now):
        minutes_until_train = (arrival_time - int(now)) // 60
        return "{}".format(minutes_until_train)

    def get_train_time_data(self, train_data):
        train_time_data = list()
        for trains in train_data:
            trip_update = trains.get('trip_update')
            if not trip_update:
                continue

            route_id = trip_update['trip']['route_id']

            stop_time_update = trip_update['stop_time_update']
            for stop_info in stop_time_update:
                if stop_info.get('stop_id') == self.station:
                    arrival = stop_info.get('arrival')
                    if not arrival:
                        continue
                    train_time_data.append((route_id, arrival['time']))
        return train_time_data

    def get_train_time_strings(self, train_time_data):
        if len(train_time_data) < 1:
            return 'no times'

        train_time_data.sort(key=lambda route_time: route_time[1])

        now = time.time()

        train_output = list()

        for i, train_arrival_time in enumerate(train_time_data[:TIMES_TO_GET]):
            train, arrival_time = train_arrival_time
            minutes_until_arrival = (arrival_time - int(now)) / 60
            if minutes_until_arrival < 1:
                continue
            if i < 1 or train_time_data[i-1][0] != train:
                train_output.append(
                    self.get_train_time_with_label(train, arrival_time, now))
            else:
                train_output.append(self.get_train_time(arrival_time, now))

        return ' '.join(train_output) + ' '

    def get_train_text(self):
        feed = self.get_feed()
        if not feed:
            # TODO log an exception
            return
        train_time_data = self.get_train_time_data(feed)
        return self.get_train_time_strings(train_time_data)

    def get_feed(self, feed_id=None):
        feed_id = feed_id or self.feed_id
        query_str = '?key={}&feed_id={}'.format(
            self.api_key, feed_id
        )
        response = requests.get(MTA_URL + query_str)

        try:
            self.feed_message.ParseFromString(response.content)
            subway_feed = protobuf_to_dict(self.feed_message)
            return subway_feed['entity']
        except DecodeError as e:
            print('Unable to decode: %s', e)
        except Exception as e:
            print(e)
            return "could not parse feed"