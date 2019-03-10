import time
import json
import enum
import aiohttp
import asyncio

import datetime 

from typing import List, Dict

from collections import namedtuple

from dank_engine_server import data_passer
import message
import device

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
        print(colour, 'has', len(stops))
        self.stop_states = [StopState(colour) for _ in range(len(stops))]

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

        self.builder = message.MessageBuilder()
        self.serial = device.SerialDevice('COM6')
        self.data = ''

    @staticmethod
    def request_train_data():
        # TODO: connect to provider server
        return data_passer.get_train_data(('SPRP', ))

    @staticmethod
    def split_line_name(name):
        return name.replace(' Line', '').replace(' line', '').split(' - ')

    def update_state(self, interval):
        print('-------------')
        print('Getting data...')
        start = datetime.datetime.now()
        data = data_passer.parse_train_data(self.data, ('SPRP', ))
        print('Parsing took', datetime.datetime.now() - start)

        for s in self.strip_states.values():
            # reset all stop LED states.
            s.clear_stops()

        for t in data:
            t = TrainData(*t)
            print()
            print(f'Handling route {t.route_id}, trip {t.trip_id}')
            s = (self.split_line_name(train_names[t.route_id]))
            
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
            
            # print(len(trip_stops[t.trip_id]))
            if len(trip_stops[t.trip_id]) > len(self.used_strips[strip]):
                print(f' WARNING: trip {t.trip_id} has more stops than LEDS on {strip}.')
                continue

            if t.stopped == 1: 
                # train is stopped. current stop is where we're at.
                cur_stop = c_prev
                strip_state.set_stop_state(cur_stop, StopModes.FLASH, 1)
            else:
                # train in motion. backtrack for previous stop.
                prev_stop = c_prev
                next_stop = c_next

                strip_state.set_stop_state(prev_stop, StopModes.NORMAL, 1-float(t.percent))
                strip_state.set_stop_state(next_stop, StopModes.NORMAL, float(t.percent))

        # print(trip_names)

    def update_arduino(self):
        print('Updating Arduino...')
        self.builder.clear_message()
        for strip, pins in self.used_strips.items():
            strip_state = self.strip_states[strip]
            for i, s_state in enumerate(strip_state.stop_states):
                # exhausted number of stops with spare pins
                pin = pins[i]
                if pin < 0 or not pin:
                    continue 

                # a single stop's state
                if s_state.intensity == 0:
                    continue
                if s_state.mode == StopModes.NORMAL:
                    cmd = message.build_fade_command(pin, s_state.colour.value, int(s_state.intensity*255))
                elif s_state.mode == StopModes.FLASH:
                    cmd = message.build_flash_command(pin, s_state.colour.value)
                else:
                    print('No command matched.')
                self.builder.add_command(cmd)
                print(i, s_state.mode, s_state.intensity)
        
        msg = self.builder.build_message()
        self.serial.send(msg)
        print(msg)


    async def loop_update(self):
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get("https://gtfsrt.api.translink.com.au/Feed/SEQ") as resp:
                    self.data = await resp.read()
                    self.update_state(10) 
                    self.update_arduino()
                    print('Done updating, waiting...')
                    await asyncio.sleep(1)


    def set_strip_for_line(self, line_and_dir, strip_pins): 
        print(f'Setting {line_and_dir} to {strip_pins}')
        self.used_strips[line_and_dir] = strip_pins

if __name__ == "__main__":
    intermediary = Intermediary() 
    intermediary.set_strip_for_line((Line.LightBlue, Direction.Northbound),
        list(range(40)))
    asyncio.run(intermediary.loop_update())