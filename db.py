from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, Text, func

engine = create_engine("sqlite:///tripwise.db", echo=True)
metaData = MetaData()

TRIPS = Table(
    "TRIPS",
    metaData,
    Column("ID", Integer, primary_key=True),
    Column("Destination", String(200), nullable=False),
    Column("Days", Integer, nullable=False),
    Column("Budget", Float, )
)

def save_trip(destination, days, budget, traveler_count, traveler_style, interests):
    # initiate id
    pass

def save_flight(trip_id, tier, airline, price, duration):
    # initiation id 
    pass

def save_hotel(trip_id, tier, name, price_per_night, rating, location):
    # initiate tier within here
    pass

def save_activity(trip_id, name, cost, category, description):
    pass

def save_plan(trip_id, plan_type, flight_id, hotel_id, total_cost, remaining_budget, itinerary_text):
    pass

def get_trip(trip_id):
    # return the trip with specified ID
    pass

def get_plans(trip_id):
    pass


