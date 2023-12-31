import xml.etree.ElementTree as ET
from datetime import datetime
import os

def find_wind_conditions(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    
    flyable_start = None
    flyable_end = None
    previous_date = None

    def convert_iso_to_datetime(iso_str):
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

    def print_flyable_time(start, end, date, location_name):
        start_time = convert_iso_to_datetime(start).strftime('%I%p').lstrip("0").lower()
        end_time = convert_iso_to_datetime(end).strftime('%I%p').lstrip("0").lower()
        formatted_date = convert_iso_to_datetime(date).strftime('%d %B')
        print(f"It's flyable at {location_name} from {start_time} to {end_time} on {formatted_date}.")

    for time_elem in root.findall(".//time"):
        from_time = time_elem.attrib["from"]
        to_time = time_elem.attrib["to"]
        
        from_hour = convert_iso_to_datetime(from_time).hour
        to_hour = convert_iso_to_datetime(to_time).hour

        # Skip times outside desired range
        if from_hour < 6 or to_hour > 23:
            continue

        date = from_time.split('T')[0]

        location_elem = time_elem.find("location")
        wind_direction_elem = location_elem.find("windDirection")
        wind_speed_elem = location_elem.find("windSpeed")

        if wind_direction_elem is not None and wind_speed_elem is not None:
            direction = float(wind_direction_elem.attrib["deg"])
            speed_mps = float(wind_speed_elem.attrib["mps"])

            if 270 <= direction <= 360 or 0 <= direction <= 90:
                if 3 <= speed_mps <= 7:
                    if flyable_start is None:
                        flyable_start = from_time
                        flyable_end = to_time
                        previous_date = date
                    elif date == previous_date and convert_iso_to_datetime(to_time) == convert_iso_to_datetime(flyable_end).replace(hour=convert_iso_to_datetime(flyable_end).hour + 1):
                        flyable_end = to_time
                    else:  
                        location_name = os.path.splitext(filename)[0]
                        print_flyable_time(flyable_start, flyable_end, previous_date, location_name)
                        flyable_start = from_time
                        flyable_end = to_time
                        previous_date = date

    # Handle the case when the last time period is flyable
    if flyable_start:
        location_name = os.path.splitext(filename)[0]
        print_flyable_time(flyable_start, flyable_end, previous_date, location_name)

if __name__ == "__main__":
    # Loop over each XML file in the directory
    for file in os.listdir("."):
        if file.endswith(".xml"):
            find_wind_conditions(file)
