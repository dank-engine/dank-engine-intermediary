import data_passer
import time
import json

from collections import namedtuple

TrainData = namedtuple('TrainData', 'trip_id route_id stop_id stopped arrival_time arrival_delay departure_time departure_delay stop_sequence')

Train = namedtuple('Train', 'stop1 stop2')

with open('trains.json') as f:
    trip_names = json.load(f)

with open('canonical_trips_to_stops.json') as f:
    trip_stops = json.load(f)

with open('canonical_stops.json') as f:
    canonical = json.load(f)

def request_train_data():
    return data_passer.get_train_data(('SPRP', ))

class Intermediary:
    def __init__(self):
        self.next_stops = {} 
        self.previous_ = {}

    def update(self, interval):
        timestamp, *data = request_train_data()
        print('Updating at', timestamp)

        trains = []

        for t in data:
            train_data = TrainData(*t)
            print(train_data)
            # canonical id for use if stop is in a station.
            can_id = canonical.get(train_data.stop_id, train_data.stop_id)
            # print(canonical[train_data.stop_id])
            cur_index = trip_stops[train_data.trip_id].index(can_id)
            if train_data.stopped == 1: 
                # train is stopped. current stop is where we're at
                cur_stop = can_id
            else:
                # train in motion. backtrack for previous stop
                prev_index = max(cur_index-1, 0)
                next_index = cur_index

        # print(trip_names)

        print('Done')

    def loop_update(self):
        while True:
            self.update(10) 
            time.sleep(10)

if __name__ == "__main__":
    Intermediary().loop_update()