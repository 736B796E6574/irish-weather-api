const startButton = document.getElementById('start-button');
const results = document.getElementById('results');

startButton.addEventListener('click', () => {
    console.log("START EVENT LISTENER");
    main();
});

// Base URL for the API
const base_url = "http://metwdb-openaccess.ichec.ie/metno-wdb2ts/locationforecast";

// Sample locations
const locations = {
    "Clara": {
        lat: 52.051486344257704,
        lon: -9.093779204800772
    },
    "Knockmealdown": {
        lat: 53.123456,
        lon: -9.123456
    }
    // Add more locations as needed
};

// Fetch weather data for a given latitude and longitude
async function fetchWeatherData(lat, lon) {
    try {
        let response = await fetch(`${base_url}?lat=${lat}&long=${lon}`);
        if (response.ok) {
            return await response.text(); // or response.json() if the response is in JSON format
        } else {
            console.error(`Error ${response.status}: ${await response.text()}`);
            return null;
        }
    } catch (error) {
        console.error(`Failed to fetch data: ${error.message}`);
        return null;
    }
}

// Iterate through each location and fetch data
async function main() {
    for (let locationName in locations) {
        let {
            lat,
            lon
        } = locations[locationName];
        let data = await fetchWeatherData(lat, lon);
        if (data) {
            // Here, instead of saving to a file, we're logging the fetched data
            console.log(`Data for ${locationName}:`, data);
        } else {
            console.error(`Failed to fetch data for ${locationName}.`);
        }
    }
}