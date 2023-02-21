"""
Program creates html file with map
"""
import argparse
import re
import haversine
import folium
from geopy.geocoders import Nominatim
def read_file(path:str, data:str) -> dict:
    """
    Function reads file
    
    """
    dict_of_films={}
    file=open(path, 'r')
    for line in file:
        set_elements=[]
        if line.find("(")!=-1:
            if not re.search(r"\((\d{4})\)",line) is None:
                set_elements.append(line[:re.search(r"\((\d{4})\)",line).start()-1])
                set_elements.append(re.search(r"\((\d{4})\)",line).group(0))
                line=line[re.search(r"\((\d{4})\)",line).end()+1:]
                line=line.strip()
                line=line.replace("(","[")
                line=line.replace(")","]")
                line=line.replace("{","[")
                line=line.replace("}","]")
                while not re.search(r"\[([\S ]+)\]",line) is None:
                    line=line.replace(re.search(r"\[([\S ]+)\]",line).group(0), "")
                line=line.strip()
                if set_elements[1]=="("+data+")":
                    if not line in dict_of_films:
                        dict_of_films[line]=set()
                    dict_of_films[line].add(set_elements[0]+" "+set_elements[1])
    dict_of_films_2={}
    for i in dict_of_films:
        geolocator = Nominatim(user_agent="UCU_student", timeout=10)
        location = geolocator.geocode(i)
        if not location is None:
            dict_of_films_2[(location.latitude, location.longitude)]=dict_of_films[i]
    return dict_of_films_2


def find_the_nearest(dict_of_films:dict, coordinates:tuple) -> list:
    """
    Function returns nearest points
    """
    new_list=list()
    for i in dict_of_films:
        temp_list=(haversine.haversine(i, coordinates), i[0], i[1])
        new_list.append(temp_list)
    new_list.sort()
    return new_list

def draw_map(dict_of_films:dict, list_of_locations:list, coordinates:tuple):
    """
    Function creates html map
    """
    map = folium.Map(location = coordinates, zoom_start=20)
    films_marker = folium.FeatureGroup(name="Films")
    for i in range(min(10, len(list_of_locations))):
        films_marker.add_child(folium.Marker(location = [list_of_locations[i][1], list_of_locations[i][2]], popup="\n".join(dict_of_films[(list_of_locations[i][1],list_of_locations[i][2])]), icon = folium.Icon()))
    country_area = folium.FeatureGroup(name="Area")
    country_area.add_child(folium.GeoJson(data=open('world.json', 'r',
                                            encoding='utf-8-sig').read(),
                                style_function=lambda x: {'fillColor':
        'cyan' if x['properties']['AREA']*10 < 3000
    else 'green' if 3000 <= x['properties']['AREA']*10.5 < 250000
    else 'yellow' if 250000 <= x['properties']['AREA']*10.5 < 1000000
    else 'orange' if 1000000 <= x['properties']['AREA']*10.5 < 3000000
    else 'red'}))
    map.add_child(films_marker)
    map.add_child(country_area)
    map.add_child(folium.LayerControl())
    map.save("Lab1_map.html")
parser=argparse.ArgumentParser(description="Function creates html map")
parser.add_argument("year", type=str,help="Year of films")
parser.add_argument("latitude", type=float,help="Latitude")
parser.add_argument("longtitude", type=float,help="Longtitude")
parser.add_argument("path", type=str,help="Path to data")
args=parser.parse_args()
year=args.year
latitude=args.latitude
longtitude=args.longtitude
path=args.path
dictionary_of_films=read_file(path, year)
list_of_locations=find_the_nearest(dictionary_of_films, (latitude, longtitude))
draw_map(dictionary_of_films, list_of_locations, [latitude, longtitude])
print("HTML file is ready!")
