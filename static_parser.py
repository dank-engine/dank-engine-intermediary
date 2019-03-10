from collections import defaultdict
import json
import enum
import csv

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

class RouteStrip(enum.Enum):
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



with open('SEQ_GTFS/trips.txt') as f:
    trips = list(csv.DictReader(f))

# with open('SEQ_GTFS/stop_times.txt') as f:
#     # stop_times = f.read()
#     trips_ = defaultdict(list)
#     for i, li in enumerate(f):
#         if i % 10000 == 0:
#             print(i)
#         l = li.split(',')
#         trips_[l[0]].append(l[3])

# with open('trip_to_stops.json', 'w') as f:
#     json.dump(trips_, f)


def find_trip_on_route(route):
    for t in trips:
        if t['route_id'] == route:
            return t['trip_id']

with open('trip_to_stops.json') as f:
    trip_to_stops = json.load(f)

def find_stops_on_trip(trip):
    return trip_to_stops[trip]

with open('SEQ_GTFS/stops.txt') as f:
    d = {}
    for l in csv.DictReader(f):
        d[l['stop_id']] = l['stop_name']
    with open('stops_to_names.json', 'w') as f2:
        json.dump(d, f2)

# all trips here are NORTHBOUND
canonical_trips = {
    RouteStrip.Green: ('RWCA-1256', 'BRGY-1167'),
    RouteStrip.Red: ('BNFG-1167', ),
    RouteStrip.LightBlue: ('SPRP-1167', ),
    RouteStrip.DarkBlue: ('CLSH-1167', ),
    RouteStrip.Yellow: ('VLBD-1167', ),
    RouteStrip.Purple: ('BRDB-1256', )
}

stops_per_route = {}

for strip, routes in canonical_trips.items():
    stops = list()
    for r in routes:
        print(strip, r)
        t = find_trip_on_route(r)
        print(t)
        # print(find_stops_on_trip(t))
        stops.extend(x for x in find_stops_on_trip(t) if x not in stops)
    stops_per_route[str(strip)] = list(stops)
    print(strip, [d[x] for x in stops])


with open('routes_to_stops.json', 'w') as f:
    json.dump(stops_per_route, f, indent=2)



stations = defaultdict(list)

with open('SEQ_GTFS/stops.txt') as f:
    for l in csv.DictReader(f):
        if l['parent_station']:
            stations[l['parent_station']].append(l['stop_id'])

with open('parent_stations.json', 'w') as f:
    json.dump(stations, f)

canonical_stops = {}
for station in stations.values():
    first_stop = station[0]
    for stop in station:
        if stop != first_stop:
            canonical_stops[stop] = first_stop
print(canonical_stops)

with open('canonical_stops.json', 'w') as f:
    json.dump(canonical_stops, f)


can_routes_to_stops = {}
for route, stops in stops_per_route.items():
    can_routes_to_stops[route] = [canonical_stops.get(s, s) for s in stops]

with open('canonical_routes_to_stops.json', 'w' ) as f:
    json.dump(can_routes_to_stops, f, indent=2)



canonical_trip_to_stops = {}
for trip, stops in trip_to_stops.items():
    canonical_trip_to_stops[trip] = [canonical_stops.get(s, s) for s in stops]

with open('canonical_trips_to_stops.json', 'w') as f:
    json.dump(canonical_trip_to_stops, f)

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

    # print(routes_to_destinations)

if __name__ == "__main__":
    main()