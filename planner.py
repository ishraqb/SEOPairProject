## Decides what goes into each plan

def build_all_plans(trip, flights, hotels):
    plans = {}
    plans["Cheapest"] = build_cheapest_plan(trip, flights, hotels)
    plans["Balanced"] = build_balanced_plan(trip, flights, hotels)
    plans["Experience-Focused"] = build_experience_plan(trip, flights, hotels)
    return plans

def build_cheapest_plan(trip, flights, hotels):
    result = {}

    result["plan_type"] = "Cheapest"
    result["flight"] = flights["cheapest"]
    result["hotel"] = hotels["cheapest"]

    base_cost = calculate_base_cost(trip, flights["cheapest"], hotels["cheapest"])

    result["base_cost"] = base_cost

    activity_budget = trip["Budget"] - base_cost

    if activity_budget < 0:
        result["warning"] = "This plan exceeds budget before activities"
    else:
        result["warning"] = None

    result["activity_budget"] = activity_budget
    result["activity_guidance"] = "Free or low-cost activities matching the interests"
    result["travel_style"] = trip["Traveler_Style"]
    result["interests"] = trip["Interests"]
    return result

def build_balanced_plan(trip, flights, hotels):
    result = {}

    result["plan_type"] = "Balanced"
    result["flight"] = flights["balanced"]
    result["hotel"] = hotels["balanced"]

    base_cost = calculate_base_cost(trip, flights["balanced"], hotels["balanced"])

    result["base_cost"] = base_cost

    activity_budget = trip["Budget"] - base_cost

    if activity_budget < 0:
        result["warning"] = "This plan exceeds budget before activities"
    else:
        result["warning"] = None

    result["activity_budget"] = activity_budget
    result["activity_guidance"] = "Balanced or average costing activities matching the interests"
    result["travel_style"] = trip["Traveler_Style"]
    result["interests"] = trip["Interests"]
    return result

def build_experience_plan(trip, flights, hotels):
    result = {}

    result["plan_type"] = "Experience-Focused"
    result["flight"] = flights["premium"]
    result["hotel"] = hotels["premium"]

    base_cost = calculate_base_cost(trip, flights["premium"], hotels["premium"])

    result["base_cost"] = base_cost

    activity_budget = trip["Budget"] - base_cost

    if activity_budget < 0:
        result["warning"] = "This plan exceeds budget before activities"
    else:
        result["warning"] = None

    result["activity_budget"] = activity_budget
    result["activity_guidance"] = "Premium or luxurious costing activities matching the interests"
    result["travel_style"] = trip["Traveler_Style"]
    result["interests"] = trip["Interests"]
    return result

def calculate_base_cost(trip, flight, hotel):
    flight_cost = flight["Price"]
    hotel_cost = hotel["Price_Per_Night"] * trip["Days"]
    total = flight_cost + hotel_cost
    return total

def is_within_budget(total_cost, budget):
    return total_cost <= budget