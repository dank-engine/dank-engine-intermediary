import json
import enum
import requests

import datetime

from typing import List, Tuple

from collections import namedtuple

from dank_engine_server import data_passer
from colour import RGBColour
from strip import LedStrip
import colour
import message
import device

TrainData = namedtuple('TrainData', 'route_id trip_id prev_stop_id \
                        next_stop_id stopped percent')

# load data from files
time_last_update = datetime.datetime.now()
print('Initialising at', time_last_update)

with open('json/trains.json') as f:
    trip_names = json.load(f)

with open('json/canonical_trips_to_stops.json') as f:
    trip_stops = json.load(f)

with open('json/canonical_stops.json') as f:
    canonical = json.load(f)

with open('json/trains.json') as f:
    train_names = json.load(f)

with open('json/canonical_routes_to_stops.json') as f:
    route_stops = json.load(f)

print('Loading data took', datetime.datetime.now() - time_last_update)


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
    'Doomben': (Line.Purple, Direction.Northbound),
    'Rosewood': (Line.Green, Direction.Southbound),
    'Gympie North': (Line.Green, Direction.Northbound),
    'Brisbane City': (Line.Purple, Direction.Southbound),
    'Varsity Lakes': (Line.Yellow, Direction.Southbound),
    'Caboolture': (Line.Green, Direction.Northbound),
    'Springfield': (Line.LightBlue, Direction.Southbound),
    'Airport': (Line.Yellow, Direction.Northbound),
    'Shorncliffe': (Line.DarkBlue, Direction.Northbound),
    'Beenleigh': (Line.Red, Direction.Southbound),
    'Cleveland': (Line.DarkBlue, Direction.Southbound)
}


class StopState(enum.Enum):
    Arriving = enum.auto()
    Stopped = enum.auto()
    Departing = enum.auto()
    Empty = enum.auto()


class Stop:
    """A stop in the QR network."""
    def __init__(self, name: str, state: StopState = StopState.Empty):
        self.name = name
        self.state = state
        # [0...1]. only used when state is Arriving/Departing
        self.percentage = 0.0


class Route:
    def __init__(self, line: Line, direction: Direction, stops):
        self.line = line
        self.direction = direction
        self.stops: List[Stop] = [Stop(stop) for stop in stops]

        print(f'{line} has {len(stops)} stops')

    def reset_stops(self):
        for s in self.stops:
            s.state = StopState.Empty

    def get_stop_by_id(self, stop_id: str):
        stop_index = [i for i, stop in enumerate(self.stops)
                      if stop.name == stop_id]
        if len(stop_index):
            return stop_index[0]
        return None

    def set_stop_state(self, stop_id: str, state: StopState,
                       percentage: float = 0):
        stop_index = self.get_stop_by_id(stop_id)

        if stop_index is None:
            return

        self.stops[stop_index].state = state
        self.stops[stop_index].percentage = percentage


class Intermediary:
    def __init__(self):
        self.builder = message.MessageBuilder()
        self.data = ''

        self.line_strip_mapping = {}

        self.routes = {}
        for _, (line, direction) in dest_to_strip.items():
            if (line, direction) not in self.routes:
                self.routes[(line, direction)] = \
                    Route(line, direction, route_stops['RouteStrip.' + line.name])

    @staticmethod
    def request_train_data():
        # TODO: connect to provider server
        return data_passer.get_train_data(('SPRP', ))

    @staticmethod
    def split_line_name(name: str):
        return name.replace(' Line', '').replace(' line', '').split(' - ')

    def update_state(self, interval: int):
        print('-------------')
        print('Getting data...')
        start = datetime.datetime.now()
        data = data_passer.parse_train_data(self.data, ('SPRP', ))
        print('Parsing took', datetime.datetime.now() - start)

        for route in self.routes.values():
            # reset all stop LED states.
            route.reset_stops()

        for t in data:
            t = TrainData(*t)
            print()
            print(f'Handling route {t.route_id}, trip {t.trip_id}')
            s = (self.split_line_name(train_names[t.route_id]))

            print(s)

            # get 2-tuple based on s[1], the train's destination.
            train_destination = dest_to_strip[s[1]]
            route = self.routes[train_destination]  # type: Route
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

            if train_destination not in self.line_strip_mapping:
                print(f' WARNING: line {train_destination} has no LED strip.')
                continue

            # print(len(trip_stops[t.trip_id]))
            # if len(trip_stops[t.trip_id]) > len(self.line_strip_mapping[train_destination]):
            #    print(f' WARNING: trip {t.trip_id} has more stops than LEDS on {strip}.')
            #    continue

            if t.stopped == 1:
                # train is stopped. current stop is where we're at.
                cur_stop = c_prev
                route.set_stop_state(cur_stop, StopState.Stopped)
            else:
                # train in motion. backtrack for previous stop.
                prev_stop = c_prev
                next_stop = c_next

                print(t.percent)
                route.set_stop_state(prev_stop, StopState.Departing, 1 - float(t.percent))
                route.set_stop_state(next_stop, StopState.Arriving, float(t.percent))
        # print(trip_names)

    def update_arduino(self):
        print('Updating Arduino...')
        self.builder.clear_message()

        line: Line
        strip: LedStrip
        for (line, direction), strip in self.line_strip_mapping.items():
            route = self.routes[(line, direction)]  # type: Route

            led_colour = line.value
            i: int
            stop: Stop
            for i, stop in enumerate(route.stops):
                if stop.state is StopState.Departing and stop.percentage < 0.2:
                    cmd = message.build_off_command(i)
                elif stop.state is StopState.Arriving or stop.state is StopState.Departing:
                    percentage = stop.percentage * 255.0
                    cmd = message.build_fade_command(i, led_colour, int(percentage))
                elif stop.state is StopState.Stopped:
                    cmd = message.build_flash_command(i, led_colour)
                elif stop.state is StopState.Empty:
                    cmd = message.build_off_command(i)
                self.builder.add_command(cmd)
                if stop.state is not StopState.Empty:
                    print(i, stop.state, stop.percentage)

        msg = self.builder.build_message()
        # self.serial.send(msg)
        print(msg)

    def loop_update(self):
        while True:
            self.data = requests.get("https://gtfsrt.api.translink.com.au/Feed/SEQ").content
            self.update_state(10)
            self.update_arduino()
            print('Done updating, waiting...')
            # await asyncio.sleep(1)

    def set_strip_for_line(self, line_and_dir: Tuple[Line, Direction], strip: LedStrip):
        print(f'Setting {line_and_dir} to {strip}')
        self.line_strip_mapping[line_and_dir] = strip


if __name__ == "__main__":
    intermediary = Intermediary()
    strip = LedStrip(40)
    intermediary.set_strip_for_line(
        (Line.LightBlue, Direction.Northbound),
        strip
    )
    intermediary.loop_update()
