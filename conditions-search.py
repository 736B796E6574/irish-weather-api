import xml.etree.ElementTree as ET

def find_wind_conditions(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    for time_elem in root.findall(".//time"):
        from_time = time_elem.attrib["from"]
        to_time = time_elem.attrib["to"]

        location_elem = time_elem.find("location")
        wind_direction_elem = location_elem.find("windDirection")
        wind_speed_elem = location_elem.find("windSpeed")

        if wind_direction_elem is not None and wind_speed_elem is not None:
            direction = float(wind_direction_elem.attrib["deg"])
            speed_mps = float(wind_speed_elem.attrib["mps"])
            speed_kmh = speed_mps * 3.6  # Conversion from m/s to km/h

            if 270 <= direction <= 360 or 0 <= direction <= 90:
                if 2.5 <= speed_mps <= 4.5:
                    print(f"It's flyable from {from_time} to {to_time}: Wind from {direction}° at {speed_kmh:.2f} km/h")

if __name__ == "__main__":
    find_wind_conditions("weather_data.xml")
