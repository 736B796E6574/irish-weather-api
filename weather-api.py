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
    latitude = 52.051486344257704
    longitude = -9.093779204800772
    
    data = asyncio.run(fetch_weather_data(latitude, longitude))
    if data:
        save_to_file(data)
        print(f"Data saved to 'weather_data.xml'")
    else:
        print("Failed to fetch data.")
