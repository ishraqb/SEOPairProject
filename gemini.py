from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

def fallback_itinerary(plan, trip):
    return f"""
    Gemini itinerary unavailable.

    Plan Type: {plan["plan_type"]}
    Destination: {trip["Destination"]}
    Days: {trip["Days"]}
    Traveler Style: {plan["travel_style"]}
    Interests: {plan["interests"]}

    Selected Flight:
    {plan["flight"]}

    Selected Hotel:
    {plan["hotel"]}

    Base Cost: ${plan["base_cost"]}
    Remaining Activity Budget: ${plan["activity_budget"]}

    Fallback Suggestion:
    Use this plan's select flight and hotel, then use the remaining budget to choose activities that match your travel style and interests. 

    You can also wait for Gemini to work later.
    """

def build_prompt(plan, trip):
    flight = plan["flight"]
    hotel = plan["hotel"]

    prompt = f"""
        You are a travel itinerary planner. 
        
        The flight, hotel, and budget decisions have already been made.

        DO NOT change:
        - Flight information
        - Hotel information
        - Base cost
        - Activity budget
        - Plan type

        Use only the information given below to generate a concise but detailed and realistic day-to-day itinerary.

        Trip Information:
        Destination: {trip["Destination"]}
        Days: {trip["Days"]}
        Traveler Count: {trip["Traveler_Count"]}
        Traveler Style: {plan["travel_style"]}
        Interests: {plan["interests"]}
        Plan Type: {plan["plan_type"]}

        Flight Information:
        Airline: {flight.get("Airline", "Not provided")}
        Price: ${flight["Price"]}
        Duration: {flight.get("Duration", "Not provided")}

        Hotel Information:
        Hotel Name: {hotel.get("Name", "Not provided")}
        Price Per Night: ${hotel["Price_Per_Night"]}
        Location: {hotel.get("Location", "Not provided")}

        Budget Information:
        Total Budget: ${trip["Budget"]}
        Base Cost (Flight + Hotel): ${plan["base_cost"]}
        Remaining Activity Budget: ${plan["activity_budget"]}

        Activity Guidance:
        {plan["activity_guidance"]}

        Instructions:
        Generate a {trip["Days"]}-day itinerary.

        Prioritize activities that match:
        1. Traveler Style
        2. Ranked Interests

        Keep all suggested activities within the remaining activity budget.

        For each day provide this structure:
        - Morning Activity
        - Afternoon Activity
        - Evening Activity
        - Suggested Food Experience

        At the end provide:
        - Estimated activity total spending
        - How this itinerary matches the traveler's style and interests

        Do not invent new flight or hotel information.
        Make sure this itinerary matches the plan type: {plan["plan_type"]}
        Make sure all itineraries are different and match the traveler.
        """
    return prompt

def generate_itinerary(api_key, plan, trip):
    if api_key is None:
        return fallback_itinerary(plan, trip)
    
    client = genai.Client(api_key=api_key)
    prompt = build_prompt(plan, trip)

    try:
        response = client.models.generate_content(
            model = "gemini-2.5-flash-lite",
            contents = prompt
        )
        return response.text
    
    except Exception as error:
        print("Could not generate Gemini itinerary")
        print(error)
        return

def print_itinerary(itinerary):
    if itinerary is None:
        print("No itinerary is available")
        return
    
    print("\nGenerated Itinerary")
    print(itinerary)

# Manual Test
if __name__ == "__main__":
    trip = {
        "Destination": "Tokyo",
        "Days": 5,
        "Budget": 2500,
        "Traveler_Count": 2,
        "Traveler_Style": "Foodie",
        "Interests": "food,culture,nightlife"
    }
    plan = {
        "plan_type": "Balanced",

        "flight": {
            "Airline": "Japan Airlines",
            "Price": 550,
            "Duration": "11h 30m"
        },

        "hotel": {
            "Name": "Tokyo Central Hotel",
            "Price_Per_Night": 140,
            "Location": "Shinjuku"
        },

        "base_cost": 1250,
        "activity_budget": 1250,

        "activity_guidance": "Balanced or average costing activities matching the interests",

        "travel_style": "Foodie",
        "interests": "food,culture,nightlife",

        "warning": None
    }
    itinerary = generate_itinerary(api_key, plan, trip)
    print(itinerary)