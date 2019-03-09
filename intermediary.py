import data_passer
import time
import json
import enum

import datetime 

from collections import namedtuple

TrainData = namedtuple('TrainData', 'timestamp trip_id route_id stop_id stopped arrival_time arrival_delay departure_time departure_delay stop_sequence')

# load data from files
s = datetime.datetime.now()
print('Initialising at', s)

with open('trains.json') as f:
    trip_names = json.load(f)

with open('canonical_trips_to_stops.json') as f:
    trip_stops = json.load(f)

with open('canonical_stops.json') as f:
    canonical = json.load(f)

with open('trains.json') as f:
    train_names = json.load(f)

with open('canonical_routes_to_stops.json') as f:
    route_stops = json.load(f)

print('Loading data took', datetime.datetime.now() - s)

def request_train_data():
    # TODO: connect to provider server
    return data_passer.get_train_data(('SPRP', ))


class Line(enum.Enum):
    Red = 0xff0000
    DarkBlue = 0x424bf4
    Yellow = 0xffff00
    Green = 0x00ff00
    LightBlue = 0x41aff4
    Purple = 0x9000ff

class Direction(enum.Enum):
    Northbound = enum.auto()
    Southbound = enum.auto()

# the 2-tuple of line colour and direction uniquely identify 
# a LED strip.

train_lines = {
    'Ipswich': (Line.Green, Direction.Northbound),
    'Ferny Grove': (Line.Red, Direction.Northbound),
    'Redcliffe Peninsula': (Line.LightBlue, Direction.Northbound),
    'Nambour': (Line.Green, Direction.Northbound),
    # 'Rail Bus SCAS closure': None,
    'Doomben': (Line.Purple, Direction.Northbound),
    'Rosewood': (Line.Green, Direction.Southbound),
    'Gympie North': (Line.Green, Direction.Northbound),
    'Brisbane City': (Line.Purple, Direction.Southbound),
    'Varsity Lakes': (Line.Yellow, Direction.Southbound),
    'Caboolture': (Line.Green, Direction.Northbound),
    'Springfield': (Line.LightBlue, Direction.Southbound),
    'Airport': (Line.Yellow, Direction.Northbound),
    # 'RAILBUS Eagle Junction': None,
    'Shorncliffe': (Line.DarkBlue, Direction.Northbound),
    'Beenleigh': (Line.Red, Direction.Southbound),
    'Cleveland': (Line.DarkBlue, Direction.Southbound)
}



class StopState(enum.Enum):
    APPROACH = enum.auto() 
    STOPPED = enum.auto() 
    LEAVING = enum.auto()

class RouteStripState:
    def __init__(self, colour, direction, stops):
        self.colour = colour 
        self.direction = direction
        self.stops = stops
        self.stop_states = [None]*len(self.stops)

    def clear_state(self):
        self.stop_states = [None]*len(self.stops)

    def set_stop_state(self, stop_id, state: StopState): 
        print(f'Setting stop {stop_id} to state {state} on {self.colour}, {self.direction}.')
        i = self.stops.index(stop_id)
        print(f' Stop index {i}')

        self.stop_states[i] = state


_route_states = {}
route_strip_states = {}
for dest, line in train_lines.items():
    if line not in _route_states:
        _route_states[line] = RouteStripState(line[0], line[1], route_stops['RouteStrip.'+line[0].name])
    route_strip_states[dest] = _route_states[line]



def split_line_name(name):
    return name.replace(' Line', '').replace(' line', '').split(' - ')

class Intermediary:
    def __init__(self):
        self.next_stop = {} 
        self.previous_time_remaining = {}

    # train_data attributes:
    # timestamp
    # trip_id
    # route_id
    # stop_id
    # stopped
    # arrival_time
    # arrival_delay
    # departure_time
    # departure_delay
    # stop_sequence

    def update(self, interval):
        data = request_train_data()
        print('Updating...')

        trains = []

        for t in data:
            t = TrainData(*t)
            print()
            print(f'Handling route {t.route_id}, trip {t.trip_id}')
            s = (split_line_name(train_names[t.route_id]))
            print(s)
            strip_state = route_strip_states[s[1]]
            # print(t)
            # if train_data.timestamp:
            #     print(train_data.arrival_time - train_data.timestamp)

            # normalised canonical id of the station platform's stop id.
            can_id = canonical.get(t.stop_id, t.stop_id)
            
            try:
                cur_index = trip_stops[t.trip_id].index(can_id)
            except IndexError:
                print(f' WARNING: No stop {can_id} on the {t.route_id} route.')
                continue
            if t.stopped == 1: 
                # train is stopped. current stop is where we're at.
                cur_stop = can_id
                strip_state.set_stop_state(cur_stop, StopState.STOPPED)
            else:
                # train in motion. backtrack for previous stop.
                prev_stop = trip_stops[t.trip_id][max(cur_index-1, 0)]
                next_stop = can_id

                strip_state.set_stop_state(prev_stop, StopState.LEAVING)
                strip_state.set_stop_state(next_stop, StopState.APPROACH)
            

        # print(trip_names)

        print('Done')

    def loop_update(self):
        while True:
            self.update(10) 
            time.sleep(10)

if __name__ == "__main__":
    Intermediary().loop_update()