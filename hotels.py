import requests
from datetime import datetime

def search_hotels(api_key, destination, checkin, checkout, travelers):
    
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    dest_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
    dest_params = {"query": destination}
    dest_response = requests.get(dest_url, headers=headers, params=dest_params)

    if dest_response.status_code != 200:
        print("Could not find destination.")
        return None
    dest_data = dest_response.json()
    results = dest_data.get("data", [])

    if not results:
        print("No destination found for: " + destination)
        return None
    
    dest_id = results[0].get("dest_id", "")
    dest_type = results[0].get("dest_type", "city")

    hotel_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
    hotel_params = {
        "dest_id": dest_id,
        "search_type": dest_type,
        "arrival_date": checkin,
        "departure_date": checkout,
        "adults": str(travelers),
        "room_qty": "1",
        "currency_code": "USD"
    }

    hotel_response = requests.get(hotel_url, headers=headers, params=hotel_params)

    if hotel_response.status_code != 200:
        print("Could not fetch hotel listings.")
        return None

    hotel_data = hotel_response.json()
    hotels = hotel_data.get("data", {}).get("hotels", [])

    if not hotels:
        print("No hotels found for that destination")
        return None
    
    hotels = [
        h for h in hotels
        if h.get("property", {}).get("priceBreakdown", {}).get("grossPrice")
    ]

    hotels.sort(key=lambda x: x["property"]["priceBreakdown"]["grossPrice"]["value"])

    def extract(hotel):
        prop = hotel.get("property", {})
        name = prop.get("name", "Unknown Hotel")
        price = prop.get("priceBreakdown", {}).get("grossPrice", {}).get("value", "N/A")
        rating = prop.get("reviewScore", "N/A")
        return {"name": name, "price": round(price), "rating": rating}

    cheapest = extract(hotels[0])
    balanced = extract(hotels[len(hotels) // 2])
    premium = extract(hotels[-1])

    return {
        "cheapest": cheapest,
        "balanced": balanced,
        "premium": premium
    }

def print_hotels(hotels):
    if hotels is None:
        print("No hotel info available.")
        return
    print("Hotel Options")
    for tier, info in hotels.items():
        print(tier.capitalize() + ":")
        print("Hotel: " + info["name"])
        print("Price: $" + str(info["price"]))
        print("Rating: " + str(info["rating"]))
