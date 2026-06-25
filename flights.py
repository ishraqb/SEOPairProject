import requests
from datetime import datetime


def search_flights(api_key, origin, destination, date, travelers):
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    def fetch(cabin_class):
        params = {
            "fromId": origin + ".AIRPORT",
            "toId": destination + ".AIRPORT",
            "departDate": date,
            "adults": str(travelers),
            "currency_code": "USD",
            "cabinClass": cabin_class
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("Could not fetch flight data.")
            return None
        data = response.json()
        return data.get("data", {}).get("flightOffers", [])

    economy_offers = fetch("ECONOMY")
    business_offers = fetch("BUSINESS")

    if not economy_offers:
        print("No flights found for that route.")
        return None

    economy_offers = [
        offer for offer in economy_offers if offer.get("priceBreakdown")
    ]
    economy_offers.sort(
        key=lambda x: x["priceBreakdown"]["totalRounded"]["units"]
    )

    def extract(offer):
        price = offer["priceBreakdown"]["totalRounded"]["units"]
        airline = offer["segments"][0]["legs"][0]["carriersData"][0]["name"]
        dep = datetime.fromisoformat(offer["segments"][0]["departureTime"])
        arr = datetime.fromisoformat(offer["segments"][0]["arrivalTime"])
        total_mins = int((arr - dep).total_seconds() / 60)
        hours = total_mins // 60
        mins = total_mins % 60
        duration = str(hours) + "h " + str(mins) + "m"
        return {"price": price, "airline": airline, "duration": duration}

    cheapest = extract(economy_offers[0])
    balanced = extract(economy_offers[len(economy_offers) // 2])

    if business_offers:
        business_offers = [
            offer for offer in business_offers if offer.get("priceBreakdown")
        ]
        business_offers.sort(
            key=lambda x: x["priceBreakdown"]["totalRounded"]["units"]
        )
        premium = extract(business_offers[0])
    else:
        premium = extract(economy_offers[-1])

    return {
        "cheapest": cheapest,
        "balanced": balanced,
        "premium": premium
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
        print("Duration: " + str(info["duration"]))
