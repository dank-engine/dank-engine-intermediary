from collections import defaultdict
import json
import enum

routes_to_strip = {} 

destinations = {
    'Ipswich': None,
    'Ferny Grove': None,
    'Redcliffe Peninsula': None,
    'Nambour': None,
    'Rail Bus SCAS closure': None,
    'Doomben': None,
    'Rosewood': None,
    'Gympie North': None,
    'Brisbane City': None,
    'Varsity Lakes': None,
    'Caboolture': None,
    'Springfield': None,
    'Airport': None,
    'RAILBUS Eagle Junction': None,
    'Shorncliffe': None,
    'Beenleigh': None,
    'Cleveland': None
}

class RouteStrip(enum):
    Red = enum.auto() 
    DarkBlue = enum.auto() 
    Yellow = enum.auto()
    Green = enum.auto() 
    LightBlue = enum.auto() 
    Purple = enum.auto() 

route_colours = {
    'Ipswich': RouteStrip.Green,
    'Ferny Grove': RouteStrip.Red,
    'Redcliffe Peninsula': RouteStrip.LightBlue,
    'Nambour': RouteStrip.Green,
    # 'Rail Bus SCAS closure': None,
    'Doomben': RouteStrip.Purple,
    'Rosewood': RouteStrip.Green,
    'Gympie North': RouteStrip.Green,
    # 'Brisbane City': RouteStrip.,
    'Varsity Lakes': RouteStrip.Yellow,
    'Caboolture': RouteStrip.Green,
    'Springfield': RouteStrip.LightBlue,
    'Airport': RouteStrip.Yellow,
    # 'RAILBUS Eagle Junction': None,
    'Shorncliffe': RouteStrip.DarkBlue,
    'Beenleigh': RouteStrip.Red,
    'Cleveland': RouteStrip.DarkBlue
}

canonical_trips = {
    RouteStrip.Green: ('RWCA-1256', 'BRGY-1167'),
    RouteStrip.Red: ('BNFG-1167', ),
    RouteStrip.LightBlue: ('RPSP-1167', ),
    RouteStrip.DarkBlue: ('SHCL-1167', ),
    RouteStrip.Yellow: ('VLBD-1167', ),
    RouteStrip.Purple: ('BRDB-1256', )
}

with open('SEQ_GTFS/trips.txt') as f:
    trips = json.load(f)

with open('SEQ_GTFS/stop_times.txt') as f:
    stop_times = json.load(f)

def find_trip_on_route(route):
    pass

for strip, routes in canonical_trips.items():




line_to_stops = {}

def main():
    with open('trains.json') as f:
        trains = json.load(f)

    destinations = set()
    routes_to_destinations = {}

    for code, name in trains.items():
        name = name.replace(' Line', '').replace(' line', '')
        routes_to_destinations[code] = name.split(' - ')
        destinations.update(routes_to_destinations[code])

    print(routes_to_destinations)

if __name__ == "__main__":
    main()