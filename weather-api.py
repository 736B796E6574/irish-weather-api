import aiohttp
import asyncio

async def fetch_weather_data(lat, lon):
    base_url = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast"
    params = {
        "lat": lat,
        "long": lon
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Error {response.status}: {await response.text()}")
                return None

def save_to_file(data, filename="weather_data.xml"):
    with open(filename, "w") as file:
        file.write(data)

if __name__ == "__main__":
    # Define locations as a dictionary: {"location_name": (latitude, longitude)}
    locations = {
        "Clara": (52.051486344257704, -9.093779204800772),
        "Knockmealdown": (53.123456, -9.123456),  # Sample data
        # Add more locations as needed
    }

    for location_name, (latitude, longitude) in locations.items():
        data = asyncio.run(fetch_weather_data(latitude, longitude))
        if data:
            filename = f"{location_name}.xml"
            save_to_file(data, filename)
            print(f"Data saved to '{filename}'")
        else:
            print(f"Failed to fetch data for {location_name}.")
