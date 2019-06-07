import airtable
import yaml
import geopy
import geopy.distance
import re, csv

API_KEY = yaml.load(open('keys.yaml').read())['noa-geo-tableau']

gmaps_pattern = re.compile(r'https://.*google\.co.*/maps/.*@(.*),(.*),.*')

# Define starting point.

# Define a general distance object, initialized with a distance of 1 km.
d = geopy.distance.VincentyDistance(kilometers = 1)

# Use the `destination` method with a bearing of 0 degrees (which is north)
# in order to go from point `start` 1 km to north.
# print d.destination(point=start, bearing=0)


def main():
    table = airtable.Airtable('appoyHh1yElcTGgLd', 'x toponimos', api_key=API_KEY)
    data = []

    for record in table.get_all():
        gmaps_link = record['fields']['Link de google maps']
        try:
            lon, lat = gmaps_pattern.match(gmaps_link).groups()[0:2]
        except:
            print(gmaps_link)
            print(gmaps_pattern.match(gmaps_link).groups())
            continue
        start = geopy.Point(lat, lon)
        card = record['fields'].get('Punto cardinal vs REF')
        if card:
            d = geopy.distance.VincentyDistance(kilometers=record['fields']['Distancia a REF (Kilometros)'])
            if card == 'Norte':
                bearing = 0
            elif card == 'Noreste':
                bearing = 90/2
            elif card == 'Este':
                bearing = 90
            elif card == 'Sureste':
                bearing = 90+90/2
            elif card == 'Sur':
                bearing = 180
            elif card == 'SurOeste':
                bearing = 180+90/2
            elif card == 'Oeste':
                bearing = 180+90

            loc = d.destination(start, bearing=bearing)
        else:
            loc = start

        data.append({'name': record['fields']['Nombre'], 'lat': loc.latitude, 'lon': loc.longitude})

    with open('out.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

main()