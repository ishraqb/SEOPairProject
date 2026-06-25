from google import genai
from dotenv import load_dotenv
from datetime import date, datetime

import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")


def fallback_itinerary(plan, trip):
    # Backup itinerary response incase gemini is busy and can't create it

    return f"""
    Server itinerary unavailable.

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
    Use this plan's selected flight and hotel
    Then use the remaining budget to choose
    activities that match your travel style and interests

    You can also wait for server to work later.
    """


def build_prompt(plan, trip):
    # Builds prompt with the details for the trip to the send to gemini

    flight = plan["flight"]
    hotel = plan["hotel"]
    start_date = trip["Start_Date"].strftime("%b %d, %Y")
    end_date = trip["End_Date"].strftime("%b %d, %Y")

    prompt = f"""
        You are a travel itinerary planner.

        The flight, hotel, and budget decisions have already been made.

        DO NOT change:
        - Flight information
        - Hotel information
        - Base cost
        - Activity budget
        - Plan type

        Use the information below as the source of truth.

        Trip Information:
        Destination: {trip["Destination"]}
        Start Date: {trip["Start_Date"]}
        End Date: {trip["End_Date"]}
        Days: {trip["Days"]}
        Traveler Count: {trip["Traveler_Count"]}
        Traveler Style: {plan["travel_style"]}
        Ranked Interests: {plan["interests"]}
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
        Generate exactly ONE itinerary for the selected plan.

        Prioritize activities that match:
        1. Traveler Style
        2. Ranked Interests

        Follow this format:

        =======================================
        {plan["plan_type"]} Plan

        Destination: {trip["Destination"]}
        Dates: {start_date} to {end_date}

        (Note: Please format the dates above like "Jun 25, 2026")

        Flight
        • Airline • Price • Duration

        Hotel
        • Name • Location
        • Price per Night

        Budget
        Total: ${trip["Budget"]}
        Base Cost (Flight + Hotel): ${plan["base_cost"]}
        Activity Budget: ${plan["activity_budget"]}

        ---------------------------------------

        Daily Itinerary

        Day 1

        Morning:
        ...

        Afternoon:
        ...

        Evening:
        ...

        Food Recommendation:
        ...

        Estimated Daily Cost:
        $...

        ---------------------------------------

        (Repeat this structure until Day {trip["Days"]}.)

        Trip Summary:

        Estimated Total Activity Spending: $...
        Estimated Remaining Budget: $...

        Why this itinerary matches the traveler's style and ranked interests:
        2-3 concise sentences explaining how it matches the
        traveler style and ranked interest

        =======================================

        Requirements:
        - Keep each activity description to 1-2 concise sentences that
        clearly describe the experience
        - Activities must be realistic for the destination
        - Activities should be geographically sensible
        - Prioritize the ranked interests in order
        - Activities should reflect the traveler's style
        - Include activity admission, local transportation,
        and food in cost estimates
        - Use realistic destination specific prices
        - Keep total activity spending within the remaining activity budget
        - For Cheapest plans, focus on budget-friendly activities
        - For Balanced plans, mix affordable and premium experiences
        - For Experience-Focused plans, prioritize memorable experiences
        while staying within budget
        - Do not invent or modify any flight information
        - Do not invent or modify any hotel information
        - Make the response easy to read in a command-line terminal
        - Avoid long paragraphs
        - Return ONLY the itinerary in the format above
        """
    return prompt


def generate_itinerary(api_key, plan, trip):
    # Send Gemini all the info to create the itinerary

    if api_key is None:
        return fallback_itinerary(plan, trip)

    client = genai.Client(api_key=api_key)
    prompt = build_prompt(plan, trip)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        return response.text

    except Exception as error:
        print("Could not generate server itinerary")
        return fallback_itinerary(plan, trip)


def print_itinerary(itinerary):
    # Print the intinerary, has a check for None

    if itinerary is None:
        print("No itinerary is available")
        return

    print("\nGenerated Itinerary")
    print(itinerary)
