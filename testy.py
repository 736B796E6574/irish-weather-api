import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

print('i work')

async def fetch_weather_data(lat, lon):
    base_url = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast"
    params = {
        "lat": lat,
        "long": lon
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                data = await response.text()
                return data
            else:
                print(f"Error {response.status}: {await response.text()}")
                return None

def convert_iso_to_datetime(iso_str, hour_adjustment=0):
    date_time = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    if hour_adjustment != 0:
        date_time += timedelta(hours=hour_adjustment)
    return date_time

def find_wind_conditions(xml_data, location_name):
    root = ET.fromstring(xml_data)
    
    flyable_start = None
    flyable_end = None
    previous_date = None
    results = []

    def convert_iso_to_datetime(iso_str):
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

    def add_flyable_time(start, end, date):
        start_time = convert_iso_to_datetime(start).strftime('%I%p').lstrip("0").lower()
        end_time = convert_iso_to_datetime(end).strftime('%I%p').lstrip("0").lower()
        formatted_date = convert_iso_to_datetime(date).strftime('%d %B')
        results.append({
            'location': location_name,
            'start_time': start_time,
            'end_time': end_time,
            'date': formatted_date
        })

    def print_flyable_time(start, end, date):
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
                        print_flyable_time(flyable_start, flyable_end, previous_date)
                        flyable_start = from_time
                        flyable_end = to_time
                        previous_date = date

    # Handle the case when the last time period is flyable
    if flyable_start:
        add_flyable_time(flyable_start, flyable_end, previous_date)

        return results

def consolidate_results(results):
    consolidated = {}
    
    for entry in results:
        location = entry['location']
        date = entry['date']
        
        if location not in consolidated:
            consolidated[location] = {}
            
        if date not in consolidated[location]:
            consolidated[location][date] = {
                'start_times': [],
                'end_times': []
            }
        
        consolidated[location][date]['start_times'].append(entry['start_time'])
        consolidated[location][date]['end_times'].append(entry['end_time'])
    
    return consolidated


if __name__ == "__main__":
    # Define locations as a dictionary: {"location_name": (latitude, longitude)}
    locations = {
        "Clara": (52.051486344257704, -9.093779204800772),
        "Knockmealdown": (53.123456, -9.123456)
    }

    all_results = []

    for location_name, (latitude, longitude) in locations.items():
        xml_data = asyncio.run(fetch_weather_data(latitude, longitude))
        if xml_data:
            results = find_wind_conditions(xml_data, location_name)
            all_results.extend(results)

    consolidated_results = consolidate_results(all_results)
    
    for location, dates in consolidated_results.items():
        for date, times in dates.items():
            time_ranges = ', '.join([f"{start}-{end}" for start, end in zip(times['start_times'], times['end_times'])])
            print(f"It's flyable at {location} on {date} during: {time_ranges}.")
    
