import requests
from datetime import datetime

def search_flights(api_key, origin, destination, date, travelers):
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    params = {
        "fromId": origin + ".AIRPORT",
        "toId": destination + ".AIRPORT",
        "departDate": date,
        "adults": str(travelers),
        "currency_code": "USD"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Could not fetch flight data.")
        return None

    data = response.json()
    offers = data.get("data", {}).get("flightOffers", [])

    if not offers:
        print("No flights found for that route.")
        return None

    offers.sort(key=lambda x: x["priceBreakdown"]["totalRounded"]["units"])

    cheapest = offers[0]
    balanced = offers[len(offers) // 2]
    premium = offers[-1]

    def extract(offer):
        price = offer["priceBreakdown"]["totalRounded"]["units"]
        airline = offer["segments"][0]["legs"][0]["carriersData"][0]["name"]
        dep = datetime.fromisoformat(offer["segments"][0]["departureTime"])
        arr = datetime.fromisoformat(offer["segments"][0]["arrivalTime"])
        duration_mins = int((arr-dep).total_seconds() / 60)
        return {"price": price, "airline": airline, "duration_mins": duration_mins}

    return {
        "cheapest": extract(cheapest),
        "balanced": extract(balanced),
        "premium": extract(premium)
    }

def print_flights(flights):
    if flights is None:
        print("No flight info available.")
        return
    print("\nFlight Options")
    for tier, info in flights.items():
        print(tier.capitalize() + ":")
        print("Airline: " + str(info["airline"]))
        print("Price: $" + str(info["price"]))
        print("Duration: " + str(info["duration_mins"]) + " minutes")
