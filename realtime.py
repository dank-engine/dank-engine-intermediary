from google.transit import gtfs_realtime_pb2
import urllib.request
# import gtfs_tripify

feed = gtfs_realtime_pb2.FeedMessage()
response = urllib.request.urlopen('https://gtfsrt.api.translink.com.au/Feed/SEQ')
feed.ParseFromString(response.read())
print(feed)