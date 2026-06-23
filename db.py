from sqlalchemy import create_engine, MetaData, Table, Column, select
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, Text, func

engine = create_engine("sqlite:///tripwise.db", echo=True)
metaData = MetaData()

""" All Table Creations for SQLite """
TRIPS = Table(
    "TRIPS",
    metaData,
    Column("ID", Integer, primary_key=True),
    Column("Destination", String(200), nullable=False),
    Column("Days", Integer, nullable=False),
    Column("Budget", Float, nullable=False),
    Column("Traveler_Count", Integer, nullable=False),
    Column("Traveler_Style", String(50), nullable=False),
    Column("Interests", String(255), nullable=False),
    Column("Created_At", DateTime, server_default=func.now()),
)
FLIGHTS = Table(
    "FLIGHTS",
    metaData,
    Column("ID", Integer, primary_key=True),
    Column("Trip_ID", Integer, ForeignKey("TRIPS.ID"), nullable=False),
    Column("Tier", String(100), nullable=False),
    Column("Airline", String(200), nullable=False),
    Column("Price", Float, nullable=False),
    Column("Duration", String(50), nullable=False),
)
HOTELS = Table(
    "HOTELS",
    metaData,
    Column("ID", Integer, primary_key=True),
    Column("Trip_ID", Integer, ForeignKey("TRIPS.ID"), nullable=False),
    Column("Tier", String(100), nullable=False),
    Column("Name", String(255), nullable=False),
    Column("Price_Per_Night", Float, nullable=False),
    Column("Rating", String(10), nullable=False),
    Column("Location", String(150), nullable=False),
)
ACTIVITIES = Table(
    "ACTIVITIES",
    metaData,
    Column("ID", Integer, primary_key=True),
    Column("Trip_ID", Integer, ForeignKey("TRIPS.ID"), nullable=False),
    Column("Name", String(200), nullable=False),
    Column("Cost", Float, nullable=False),
    Column("Category", String(100), nullable=False),
    Column("Description", Text, nullable=False),
)
PLANS = Table(
    "PLANS",
    metaData,
    Column("ID", Integer, primary_key=True),
    Column("Trip_ID", Integer, ForeignKey("TRIPS.ID"), nullable=False),
    Column("Plan_Type", String(50), nullable=False),
    Column("Flight_ID", Integer, ForeignKey("FLIGHTS.ID"), nullable=False),
    Column("Hotel_ID", Integer, ForeignKey("HOTELS.ID"), nullable=False),
    Column("Total_Cost", Float, nullable=False),
    Column("Remaining_Budget", Float, nullable=False),
    Column("Itinerary_Text", Text, nullable=False),
)
PLAN_ACTIVITIES = Table(
    "PLAN_ACTIVITIES",
    metaData,
    Column("ID", Integer, primary_key=True),
    Column("Plan_ID", Integer, ForeignKey("PLANS.ID"), nullable=False),
    Column("Activity_ID", Integer, ForeignKey("ACTIVITIES.ID"), nullable=False),
    Column("Day_Number", Integer, nullable=False)
)

""" Initialize the database using all the created tables """
def init_db():
    metaData.create_all(engine)

""" Save trip to database. Returns trip_id """
def save_trip(destination, days, budget, traveler_count, traveler_style, interests):
    trip_data = {
        "Destination" : destination,
        "Days" : days,
        "Budget" : budget,
        "Traveler_Count" : traveler_count,
        "Traveler_Style" : traveler_style,
        "Interests" : interests
    }
    with engine.connect() as connection:
        result = connection.execute(TRIPS.insert().values(trip_data))
        connection.commit()
    
        new_id = result.inserted_primary_key[0]
        return new_id

""" Save flight to database. Returns flight_id """
def save_flight(trip_id, tier, airline, price, duration):
    flight_data = {
        "Trip_ID" : trip_id,
        "Tier" : tier,
        "Airline": airline,
        "Price" : price,
        "Duration" : duration
    }
    with engine.connect() as connection:
        result = connection.execute(FLIGHTS.insert().values(flight_data))
        connection.commit()

        new_id = result.inserted_primary_key[0]
        return new_id

""" Save hotel to database. Returns hotel_id """
def save_hotel(trip_id, tier, name, price_per_night, rating, location):
    hotel_data = {
        "Trip_ID" : trip_id,
        "Tier" : tier,
        "Name" : name,
        "Price_Per_Night" : price_per_night,
        "Rating" : rating,
        "Location" : location
    }

    with engine.connect() as connection:
        result = connection.execute(HOTELS.insert().values(hotel_data))
        connection.commit()

        new_id = result.inserted_primary_key[0]
        return new_id

""" Save activity to database. Returns activity_id """
def save_activity(trip_id, name, cost, category, description):
    activity_data = {
        "Trip_ID" : trip_id,
        "Name" : name,
        "Cost" : cost,
        "Category" : category,
        "Description" : description,
    }

    with engine.connect() as connection:
        result = connection.execute(ACTIVITIES.insert().values(activity_data))
        connection.commit()

        new_id = result.inserted_primary_key[0]
        return new_id

""" Save plan to database. Returns plan_id """
def save_plan(trip_id, plan_type, flight_id, hotel_id, total_cost, remaining_budget, itinerary_text):
    plan_data = {
        "Trip_ID" : trip_id,
        "Plan_Type" : plan_type,
        "Flight_ID" : flight_id,
        "Hotel_ID" : hotel_id,
        "Total_Cost" : total_cost,
        "Remaining_Budget" : remaining_budget,
        "Itinerary_Text" : itinerary_text
    }

    with engine.connect() as connection:
        result = connection.execute(PLANS.insert().values(plan_data))
        connection.commit()

        new_id = result.inserted_primary_key[0]
        return new_id

""" Add activity to plan. Returns activity_id """ 
def add_activity_to_plan(plan_id, activity_id, day_number):
    activity_to_add = {
        "Plan_ID" : plan_id,
        "Activity_ID": activity_id,
        "Day_Number": day_number
    }

    with engine.connect() as connection:
        result = connection.execute(PLAN_ACTIVITIES.insert().values(activity_to_add))
        connection.commit()

        new_id = result.inserted_primary_key[0]
        return new_id

""" Returns the trip information in dictionary format """
def get_trip(trip_id):
    res = select(TRIPS).where(TRIPS.c.ID == trip_id)
    with engine.connect() as connection:
        result = connection.execute(res)
        row = result.fetchone()
        if row is None:
            return None
        return dict(row._mapping)
    
""" Returns flight information in dictionary format """
def get_flight(flight_id):
    res = select(FLIGHTS).where(FLIGHTS.c.ID == flight_id)
    with engine.connect() as connection:
        result = connection.execute(res)
        row = result.fetchone()
        if row is None:
            return None
        return dict(row._mapping)

""" Returns hotel information in dictionary format """
def get_hotel(hotel_id):
    res = select(HOTELS).where(HOTELS.c.ID == hotel_id)
    with engine.connect() as connection:
        result = connection.execute(res)
        row = result.fetchone()
        if row is None:
            return None
        return dict(row._mapping)

""" Returns plan activities in dictionary format """
def get_plan_activities(plan_id):
    res = select(PLAN_ACTIVITIES).where(PLAN_ACTIVITIES.c.Plan_ID == plan_id)
    with engine.connect() as connection:
        result = connection.execute(res)
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

""" Returns activity and all its information in dictionary format """
def get_activity(activity_id):
    res = select(ACTIVITIES).where(ACTIVITIES.c.ID == activity_id)
    with engine.connect() as connection:
        result = connection.execute(res)
        row = result.fetchone()
        if row is None:
            return None
        return dict(row._mapping)

""" Returns plan information in dictionary format """
def get_plan(plan_id):
    res = select(PLANS).where(PLANS.c.ID == plan_id)
    with engine.connect() as connection:
        result = connection.execute(res)
        row = result.fetchone()
        if row is None:
            return None
        return dict(row._mapping)

""" Returns all plans for given trip_id in dictionary format """
def get_plans(trip_id):
    res = select(PLANS).where(PLANS.c.Trip_ID == trip_id)
    with engine.connect() as connection:
        result = connection.execute(res)
        rows = result.fetchall()
        res = []
        for row in rows:
            res.append(dict(row._mapping))
        return res
    
def get_plan_details(plan_id):
    plan = get_plan(plan_id)
    if plan is None:
        return None
    trip = get_trip(plan["Trip_ID"])
    flight = get_flight(plan["Flight_ID"])
    hotel = get_hotel(plan["Hotel_ID"])
    activities = get_plan_activities(plan_id)
    full_activity_list = []
    for activity in activities:
        a = get_activity(activity["Activity_ID"])
        if a is None:
            return None
        a["Day_Number"] = activity["Day_Number"]
        full_activity_list.append(a)

    return {
        "plan": plan,
        "trip" : trip,
        "flight" : flight,
        "hotel" : hotel,
        "activities" : full_activity_list
    }

# if __name__ == "__main__":
#     init_db()

#     trip_id = save_trip(
#         "Tokyo",
#         5,
#         2500,
#         2,
#         "Foodie",
#         "food, culture"
#     )
#     flight_id = save_flight(
#         trip_id,
#         "Balanced",
#         "Frontier",
#         25.00,
#         "12h 5min"
#     )
#     hotel_id = save_hotel(
#         trip_id,
#         "Balanced",
#         "Marriott",
#         55,
#         "8.5/10",
#         "Glendale"
#     )
#     plan_id = save_plan(
#         trip_id,
#         "Balanced",
#         flight_id,
#         hotel_id,
#         275,
#         225,
#         "Day 1: Visit downtown. Day 2: Try local food 3: Explored and relax"
#     )
#     activity_id = save_activity(
#         trip_id,
#         "Walk to the park",
#         0,
#         "Adventure",
#         "National park of the ducks"
#     )

#     add_activity_to_plan(plan_id, activity_id, 1)
#     print(get_plans(trip_id))
#     print(get_plan_details(plan_id))
    


