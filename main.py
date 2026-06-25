import re
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

import db
import flights as flight_module
import hotels as hotel_module
import gemini as gemini_module
import planner as planner_module

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
MAGENTA = "\033[95m"


def normalize_flight(f):
    return {
        "Price": f["price"],
        "Airline": f["airline"],
        "Duration": f["duration"]
    }


def normalize_hotel(h, destination):
    return {
        "Name": h["name"],
        "Price_Per_Night": h["price"],
        "Rating": h["rating"],
        "Location": destination
    }


def format_markdown(text):
    text = re.sub(r'\*\*(.*?)\*\*', BOLD + r'\1' + RESET, text)
    return text


def show_history():
    trips = db.get_all_trips()
    if not trips:
        print(YELLOW + "No past trips found." + RESET)
        return
    print(CYAN + BOLD + "\nTrip History" + RESET)
    print(WHITE + "=" * 40 + RESET)
    for trip in trips:
        print(
            CYAN + "\nTrip #" + str(trip["ID"]) + ": " +
            trip["Destination"] + RESET
        )
        print(
            GREEN + "  Dates:     " + RESET +
            str(trip["Start_Date"]) + " to " + str(trip["End_Date"])
        )
        print(GREEN + "  Budget:    " + RESET + "$" + str(trip["Budget"]))
        print(GREEN + "  Style:     " + RESET + trip["Traveler_Style"])
        print(GREEN + "  Interests: " + RESET + trip["Interests"])


def print_plan(plan_name, plan, itinerary):
    print(CYAN + BOLD + "\n" + "=" * 50 + RESET)
    print(CYAN + BOLD + "  " + plan_name + " Plan" + RESET)
    print(CYAN + BOLD + "=" * 50 + RESET)
    if plan.get("warning"):
        print(RED + "  WARNING: " + plan["warning"] + RESET)
    print(CYAN + "\nFlight:" + RESET)
    print(GREEN + "  Airline:  " + RESET + plan["flight"]["Airline"])
    print(GREEN + "  Price:    " + RESET + "$" + str(plan["flight"]["Price"]))
    print(GREEN + "  Duration: " + RESET + plan["flight"]["Duration"])
    print(CYAN + "\nHotel:" + RESET)
    print(GREEN + "  Name:          " + RESET + plan["hotel"]["Name"])
    print(
        GREEN + "  Price/Night:   " + RESET +
        "$" + str(plan["hotel"]["Price_Per_Night"])
    )
    print(GREEN + "  Rating:        " + RESET + str(plan["hotel"]["Rating"]))
    print(CYAN + "\nCosts:" + RESET)
    print(
        GREEN + "  Base Cost (flight + hotel): " + RESET +
        "$" + str(plan["base_cost"])
    )
    activity_budget = plan["activity_budget"]
    if activity_budget < 0:
        print(
            RED + "  Over budget by: $" +
            str(abs(activity_budget)) + RESET
        )
    else:
        print(
            GREEN + "  Remaining Activity Budget:  " + RESET +
            "$" + str(activity_budget)
        )
    print(CYAN + "\nItinerary:" + RESET)
    print(format_markdown(itinerary))


def main():
    load_dotenv()
    api_key = os.getenv("RAPIDAPI_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    db.init_db()

    if "--history" in sys.argv:
        show_history()
        return

    print(CYAN + BOLD + "\nWelcome to TripWise!" + RESET)
    print(WHITE + "=" * 40 + RESET)
    print(MAGENTA + "Plan your perfect trip in seconds." + RESET)
    print(
        MAGENTA +
        "Tell us where you're going and we'll build 3 personalized" +
        " plans — cheapest, balanced, and experience-focused." +
        RESET
    )
    print("")

    origin = input(YELLOW + "Departure airport code (e.g. JFK): " + RESET)
    origin = origin.strip().upper()
    destination = input(
        YELLOW + "Destination airport code (e.g. LHR): " + RESET
    )
    destination = destination.strip().upper()
    start_date = input(
        YELLOW + "Departure date (YYYY-MM-DD): " + RESET
    ).strip()
    end_date = input(
        YELLOW + "Return date (YYYY-MM-DD): " + RESET
    ).strip()
    budget = float(input(
        YELLOW + "Total budget in USD: " + RESET
    ).strip())
    travelers = int(input(
        YELLOW + "Number of travelers: " + RESET
    ).strip())
    style = input(
        YELLOW + "Your travel style (e.g. foodie, adventure, relaxed): " +
        RESET
    ).strip()
    interests = input(
        YELLOW + "Interests, comma-separated (e.g. food,culture,art): " + RESET
    ).strip()

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end_dt - start_dt).days

    if days <= 0:
        print(RED + "Error: return date must be after departure date." + RESET)
        return

    print(
        CYAN + "\nSearching flights from " + origin +
        " to " + destination + "..." + RESET
    )
    raw_flights = flight_module.search_flights(
        api_key, origin, destination, start_date, travelers
    )
    if raw_flights is None:
        print(RED + "Could not retrieve flight data. Exiting." + RESET)
        return

    print(CYAN + "Searching hotels in " + destination + "..." + RESET)
    raw_hotels = hotel_module.search_hotels(
        api_key, destination, start_date, end_date, travelers
    )
    if raw_hotels is None:
        print(RED + "Could not retrieve hotel data. Exiting." + RESET)
        return

    norm_flights = {
        tier: normalize_flight(f) for tier, f in raw_flights.items()
    }
    norm_hotels = {
        tier: normalize_hotel(h, destination) for tier, h in raw_hotels.items()
    }

    trip_id = db.save_trip(
        destination, start_dt.date(), end_dt.date(),
        days, budget, travelers, style, interests
    )

    trip_dict = {
        "Destination": destination,
        "Start_Date": start_dt.date(),
        "End_Date": end_dt.date(),
        "Days": days,
        "Budget": budget,
        "Traveler_Count": travelers,
        "Traveler_Style": style,
        "Interests": interests
    }

    print(CYAN + BOLD + "\nBuilding your 3 personalized trip plans...\n" + RESET)
    plans = planner_module.build_all_plans(trip_dict, norm_flights, norm_hotels)

    for plan_name, plan in plans.items():
        flight = plan["flight"]
        hotel = plan["hotel"]

        flight_id = db.save_flight(
            trip_id, plan["plan_type"],
            flight["Airline"], flight["Price"], flight["Duration"]
        )
        hotel_id = db.save_hotel(
            trip_id, plan["plan_type"],
            hotel["Name"], hotel["Price_Per_Night"],
            hotel["Rating"], hotel["Location"]
        )

        itinerary = gemini_module.generate_itinerary(gemini_key, plan, trip_dict)
        if itinerary is None:
            itinerary = gemini_module.fallback_itinerary(plan, trip_dict)

        db.save_plan(
            trip_id, plan["plan_type"], flight_id, hotel_id,
            plan["base_cost"], plan["activity_budget"], itinerary
        )

        print_plan(plan_name, plan, itinerary)

    print(CYAN + BOLD + "\nAll 3 plans saved. Trip #" + str(trip_id) + RESET)
    print(WHITE + "Run 'TripWise --history' to view past trips." + RESET)


if __name__ == "__main__":
    main()
