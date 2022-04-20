import requests
from urllib.parse import urlencode
import googlemaps
import json

google_api_key = API_KEY

class GoogleSearchClient(object):
    api_key = None
    lat = None
    long = None
    address_query = None
    text_query = None
    radius = None

    def __init__(self, api_key=None, address=None):
        #super().__init__()
        if api_key == None:
            raise Exception("API Key is required")

        self.api_key = api_key
        self.address_query = address

        if self.address_query != None:
            self.lat, self.long = self.geocode_address()

    def geocode_address(self):
        gmaps = googlemaps.Client(key=self.api_key)

        geocode_result = gmaps.geocode(self.address_query)

        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']

        return lat, lng

    def search_nearby(self, text_query=None, radius=None):
        self.text_query = text_query
        self.radius = radius

        nearby_search_base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

        params = {
            "key" : self.api_key,
            "location" : f"{self.lat},{self.long}",
            "keyword" : self.text_query,
            "radius" : self.radius
        }
        url_params = urlencode(params)
        url_endpoint = f"{nearby_search_base_url}?{url_params}"
        response = requests.get(url_endpoint)

        return response.json()
        

client = GoogleSearchClient(api_key=google_api_key, address=input("Enter an address: "))

search_results = client.search_nearby(text_query=input("Search: "), radius=8000)

# Convert search results to GeoJSON
geojs={
     "type": "FeatureCollection",
     "features":[
           {
                "type":"Feature",
                "geometry": {
                "type":"Point",
                "coordinates":[res["geometry"]["location"]['lat'], res["geometry"]["location"]['lng']],
            },
                "properties":{
                    "name" : res["name"],
                    "rating" : res["rating"],
                    "vicinity" : res["vicinity"],
                    "business_status" : res["business_status"]
                },
        
        } for res in search_results['results']
    ]
}

# Output GeoJSON to file in working directory
output_file = open("%s_results.json" % (str(client.text_query)), "w", encoding="utf-8")

json.dump(geojs, output_file)

output_file.close()
