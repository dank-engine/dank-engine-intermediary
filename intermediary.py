import time
import json
import enum

import datetime 

from typing import List, Dict

from collections import namedtuple

from dank_engine_server import data_passer

TrainData = namedtuple('TrainData', 'route_id trip_id prev_stop_id next_stop_id stopped percent')

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

dest_to_strip = {
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

class StopModes(enum.Enum):
    NORMAL = enum.auto() 
    FLASH = enum.auto()


class StopState():
    def __init__(self, colour):
        self.colour = colour
        self.reset() 

    def reset(self):
        self.mode = StopModes.NORMAL
        self.intensity = 0

    def set_state(self, mode, intensity):
        self.mode = mode
        self.intensity = intensity

class RouteStripState:
    def __init__(self, colour, direction, stops):
        self.colour = colour 
        self.direction = direction
        self.stops = stops
        self.stop_states = [StopState(colour)]

    def clear_stops(self):
        for s in self.stop_states:
            s.reset()

    def set_stop_state(self, stop_id, mode, intensity): 
        print(f'Setting stop {stop_id} to mode {mode} ({intensity}) on {self.colour}, {self.direction}.')
        i = self.stops.index(stop_id)
        print(f' Stop index {i}')

        self.stop_states[i].set_state(mode, intensity)
    

class Intermediary:
    def __init__(self):
        self.strip_states = {}
        for dest, line in dest_to_strip.items():
            if line not in self.strip_states:
                self.strip_states[line] = RouteStripState(line[0], line[1], route_stops['RouteStrip.'+line[0].name])

        # mapping of 2-tuple (line, direction) to a list of pin numbers.
        self.used_strips = {}

    @staticmethod
    def request_train_data():
        # TODO: connect to provider server
        return data_passer.get_train_data(('SPRP', ))

    @staticmethod
    def split_line_name(name):
        return name.replace(' Line', '').replace(' line', '').split(' - ')

    def update_state(self, interval):
        data = self.request_train_data()
        print('Updating...')

        for s in self.strip_states.values():
            # reset all stop LED states.
            s.clear_stops()

        for t in data:
            t = TrainData(*t)
            print()
            print(f'Handling route {t.route_id}, trip {t.trip_id}')
            s = (self.split_line_name(train_names[t.route_id]))
            print(s)
            # get 2-tuple based on s[1], the train's destination.
            strip = dest_to_strip[s[1]]
            strip_state = self.strip_states[strip]
            # print(t)
            # if train_data.timestamp:
            #     print(train_data.arrival_time - train_data.timestamp)

            # normalised canonical id of the station platform's stop id.
            c_prev = canonical.get(t.prev_stop_id, t.prev_stop_id)
            c_next = canonical.get(t.next_stop_id, t.next_stop_id)
            try:
                pass
                # cur_index = trip_stops[t.trip_id].index(can_id)
            except IndexError:
                print(f' WARNING: No stop {can_id} on the {t.route_id} route.')
                continue

            if strip not in self.used_strips:
                print(f' WARNING: line {strip} has no LED strip.')
                continue

            if len(trip_stops[t.trip_id]) > len(self.used_strips[strip]):
                print(f' WARNING: trip {t.trip_id} has more stops than LEDS on {strip}.')
                continue

            if t.stopped == 1: 
                # train is stopped. current stop is where we're at.
                cur_stop = c_prev
                strip_state.set_stop_state(cur_stop, StopState.STOPPED)
            else:
                # train in motion. backtrack for previous stop.
                prev_stop = c_prev
                next_stop = c_next

                strip_state.set_stop_state(prev_stop, StopState.LEAVING)
                strip_state.set_stop_state(next_stop, StopState.APPROACH)

        # print(trip_names)

        print('Done')

    def update_arduino(self):
        print('Updating Arduino...')
        pass

    def loop_update(self):
        while True:
            self.update_state(10) 
            self.update_arduino()
            time.sleep(10)

    def set_strip_for_line(self, line_and_dir, strip_pins): 
        self.used_strips[line_and_dir] = strip_pins

if __name__ == "__main__":
    intermediary = Intermediary() 
    intermediary.loop_update()