import csv 
import json

def parse_data():
    data = {}
    for file_name in ('stops', 'routes', 'trips'):
        with open(f'SEQ_GTFS/{file_name}.txt') as f:
            data[file_name] = list(csv.DictReader(f)) 

    return data

def main():
    d = parse_data()
    routes, trips, stops = d['routes'], d['trips'], d['stops']


    with open('trains.json', 'w') as f:
        json.dump({r['route_id']:r['route_long_name'] for r in routes if r['route_type'] == '2'}, f)

    trip_routes = {}

    with open('SEQ_GTFS/trips.txt') as f:
        for i, line in enumerate(f):
            if i == 0: continue
            l = line.split(',')
            trip, route = l[2], l[0]
            
            trip_routes[trip] = route
    # print(trip_routes)

    with open('trip_routes.json', 'w') as f:
        json.dump(trip_routes, f)

    print(list(sorted(set(trip_routes.values()))))


    # for s_time in stop_times:




if __name__ == "__main__":
    main()