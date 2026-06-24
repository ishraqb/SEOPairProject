import argparse
import os
from datetime import datetime
from dotenv import load_dotenv

import db
import flights as flight_module
import hotels as hotel_module
import gemini as gemini_module
import planner as planner_module

def normalize_flight(f):
    return{
        "Price" : f["price"],
        "Airline": f["airline"],
        "Duration": f["duration"]
    }

def normalize_hotel(h, destination):
    return{
        "Name": h["name"],
        "Price_Per_Night": h["price"],
        "Rating": h["rating"],
        "Location": destination
    }

def show_history():
    trips = db.get_all_trips()
    if not trips:
        print("No past trips found.")
        return
    print("Trip History")
    for trip in trips:
        print("\nTrip #" + str(trip["ID"]) + ": " + trip["Destination"])
        print("  Days:      " + str(trip["Days"]))
        print("  Budget:    $" + str(trip["Budget"]))
        print("  Style:     " + trip["Traveler_Style"])
        print("  Interests: " + trip["Interests"])

def print_plan(plan_name, plan, itinerary):
    print("\n" + "=" * 50)
    print("  " + plan_name + " Plan")
    print("=" * 50)
    if plan.get("warning"):
        print("  WARNING: " + plan["warning"])
    print("\nFlight:")
    print("  Airline:  " + plan["flight"]["Airline"])
    print("  Price:    $" + str(plan["flight"]["Price"]))
    print("  Duration: " + plan["flight"]["Duration"])
    print("\nHotel:")
    print("  Name:          " + plan["hotel"]["Name"])
    print("  Price/Night:   $" + str(plan["hotel"]["Price_Per_Night"]))
    print("  Rating:        " + str(plan["hotel"]["Rating"]))
    print("\nCosts:")
    print("  Base Cost (flight + hotel): $" + str(plan["base_cost"]))
    print("  Remaining Activity Budget:  $" + str(plan["activity_budget"]))
    print("\nItinerary:")
    print(itinerary)
        
def main():
    load_dotenv()
    api_key = os.getenv("RAPIDAPI_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    parser = argparse.ArgumentParser(description="TripWise - Smart Trip Planner")
    parser.add_argument("--origin", help="Origin airport code (e.g. JFK)")
    parser.add_argument("--destination", help="Destination city (e.g. London)")
    parser.add_argument("--start", help="Departure date (YYYY-MM-DD)")
    parser.add_argument("--end", help="Return date (YYYY-MM-DD)")
    parser.add_argument("--budget", type=float, help="Total budget in USD")
    parser.add_argument("--travelers", type=int, default=1, help="Number of travelers")
    parser.add_argument("--style", help="Travel style: foodie, adventure, or relaxed")
    parser.add_argument("--interests", help="Ranked interests, comma-separated (e.g. food, culture, art)")
    parser.add_argument("--history", action="store_true", help="View all past trips")

    args = parser.parse_args()
    db.init_db()
    
    if args.history:
        show_history()
        return
    
    required = ["origin", "destination", "start", "end", "budget", "style", "interests"]
    for req in required:
        if getattr(args, req) is None:
            print("Error: --" + req + " is required")
            parser.print_help()
            return
    
    origin = args.origin.upper()
    destination = args.destination
    start_date = args.start
    end_date = args.end
    budget = args.budget
    travelers = args.travelers
    style = args.style
    interests = args.interests

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end_dt - start_dt).days

    if days <= 0:
        print("Error: --end must be after --start.")
        return
    
    print("\nSearching flights from " + origin + " to " + destination + "...")
    raw_flights = flight_module.search_flights(api_key, origin, destination, start_date, travelers)
    if raw_flights is None:
        print("Could not retrieve flight data. Exiting.")
        return

    print("Searching hotels in " + destination + "...")
    raw_hotels = hotel_module.search_hotels(api_key, destination, start_date, end_date, travelers)
    if raw_hotels is None:
        print("Could not retrieve hotel data. Exiting.")
        return

    norm_flights = {tier: normalize_flight(f) for tier, f in raw_flights.items()}
    norm_hotels = {tier: normalize_hotel(h, destination) for tier, h in raw_hotels.items()}

    trip_id = db.save_trip(destination, days, budget, travelers, style, interests)

    trip_dict = {
        "Destination": destination,
        "Days": days,
        "Budget": budget,
        "Traveler_Count": travelers,
        "Traveler_Style": style,
        "Interests": interests
    }

    print("\nBuilding your 3 personalized trip plans...\n")
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
            hotel["Name"], hotel["Price_Per_Night"], hotel["Rating"], hotel["Location"]
        )

        itinerary = gemini_module.generate_itinerary(gemini_key, plan, trip_dict)
        if itinerary is None:
            itinerary = gemini_module.fallback_itinerary(plan, trip_dict)

        db.save_plan(
            trip_id, plan["plan_type"], flight_id, hotel_id,
            plan["base_cost"], plan["activity_budget"], itinerary
        )

        print_plan(plan_name, plan, itinerary)

    print("\nAll 3 plans saved. Trip #" + str(trip_id))
    print("Run with --history to view past trips.")


if __name__ == "__main__":
    main()
    