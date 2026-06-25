import unittest
from datetime import date
from planner import *
from db import *
from gemini import *
import os

class TestTripWise(unittest.TestCase):

    def setUp(self):
        self.trip = {
            "person1" : {
                "Destination" : "Tokyo",
                "Start_Date" : date(2026, 1, 1),
                "End_Date" : date(2026, 1, 5),
                "Days" : 4,
                "Budget" : 2000,
                "Traveler_Count" : 1,
                "Traveler_Style" : "Foodie",
                "Interests" : "Hiking, Swimming, Running"
            },
            "person2" : {
                "Destination" : "Tokyo",
                "Start_Date" : date(2026, 1, 1),
                "End_Date" : date(2026, 1, 5),
                "Days" : 4,
                "Budget" : 2000,
                "Traveler_Count" : 1,
                "Traveler_Style" : "Beach person",
                "Interests" : "Swimming, Surfing"
            },
            "person3": {
                "Destination" : "Tokyo",
                "Start_Date" : date(2026, 1, 1),
                "End_Date" : date(2026, 1, 5),
                "Days" : 4,
                "Budget" : 2000,
                "Traveler_Count" : 1,
                "Traveler_Style" : "Adventurer",
                "Interests" : "Hiking, Rock Climbing, Bouldering" 
            }
        }
        self.flights = {
            "cheapest" : {
                "Tier": "Cheapest",
                "Airline": "Delta Airlines",
                "Price": 350,
                "Duration": "2h 10m"
            },
            "balanced" : {
                "Tier" : "Balanced",
                "Airline" : "United Airlines",
                "Price" : 500,
                "Duration" : "2h 00m"
            },
            "premium" : {
                "Tier" : "Premium",
                "Airline" : "United Airlines",
                "Price" : 900,
                "Duration" : "1h 45m"
            }
        }
        self.hotels = {
            "cheapest" : {
                "Tier" : "Cheapest",
                "Name" : "Marriott Tokyo",
                "Price_Per_Night" : 55.5,
                "Rating" : "7.8/10",
                "Location" : "Downtown Tokyo"
            },
            "balanced" : {
                "Tier" : "Balanced",
                "Name" : "Marriot Upper Tokyo",
                "Price_Per_Night" : 75,
                "Rating" : "9/10",
                "Location" : "Central Tokyo"
            },
            "premium" : {
                "Tier" : "Premium",
                "Name" : "Marriot Skyland Tokyo",
                "Price_Per_Night" : 100,
                "Rating" : "9.9/10",
                "Location" : "Skyland Tokyo"
            }
        }

        self.plan = {
            "cheapest" : {
                "plan_type" : "Cheapest",
                "flight" : self.flights["cheapest"],
                "hotel" : self.hotels["cheapest"],
                "base_cost" : 572,
                "activity_budget" : 1428,
                "activity_guidance" : "Free or low-cost activities matching the interests",
                "travel_style" : "Foodie",
                "interests" : "Hiking, Swimming, Running",
                "warning" : None
            },
            "balanced" : {
                "plan_type" : "Balanced",
                "flight" : self.flights["balanced"],
                "hotel" : self.hotels["balanced"],
                "base_cost" : 800,
                "activity_budget" : 1200,
                "activity_guidance" : "Balanced or average costing activities matching the interests",
                "travel_style" : "Beach person",
                "interests" : "Swimming, Surfing",
                "warning" : None
            },
            "premium" : {
                "plan_type" : "Experience-Focused",
                "flight" : self.flights["premium"],
                "hotel" : self.hotels["premium"],
                "base_cost" : 1300,
                "activity_budget" : 700,
                "activity_guidance" : "Premium or luxurious costing activities matching the interests",
                "travel_style" : "Adventurer",
                "interests" : "Hiking, Rock Climbing, Bouldering",
                "warning" : None
            }
        }
        self.activities = [
            {
                "Name" : "Tokyo Food Market",
                "Cost" : 25,
                "Category" : "Food",
                "Description" : "Explore local street food vendors."
            },
            {
                "Name" : "Ueno Park",
                "Cost" : 0,
                "Category" : "Outdoors",
                "Description" : "Public park with walking trails."
            }
        ]

    # Planner Tests

    def test_calculate_base_cost(self):
    
        total = calculate_base_cost(self.trip["person1"], self.flights["cheapest"], self.hotels["cheapest"])
        self.assertEqual(total, 572)

    def test_is_within_budget_true(self):

        result = is_within_budget(750, self.trip["person1"]["Budget"])
        self.assertTrue(result)

    def test_is_within_budget_false(self):
        
        result = is_within_budget(3000, self.trip["person1"]["Budget"])
        self.assertFalse(result)

    def test_build_cheapest_plan(self):

        plan = build_cheapest_plan(
            self.trip["person1"],
            self.flights,
            self.hotels,
        )

        self.assertEqual(self.plan["cheapest"], plan)

    def test_build_balanced_plan(self):

        plan = build_balanced_plan(
            self.trip["person2"],
            self.flights,
            self.hotels
        )

        self.assertEqual(self.plan["balanced"], plan)

    def test_build_experience_plan(self):

        plan = build_experience_plan(
            self.trip["person3"],
            self.flights,
            self.hotels
        )

        self.assertEqual(self.plan["premium"], plan)


    # Gemini Tests

    def test_build_prompt(self):
        prompt = build_prompt(self.plan["cheapest"], self.trip["person1"])

        self.assertIn("You are a travel itinerary planner.", prompt)
        self.assertIn("Tokyo", prompt)
        self.assertIn("Cheapest Plan", prompt)
        self.assertIn("Delta Airlines", prompt)
        self.assertIn("$350", prompt)
        self.assertIn("Marriott", prompt)
        self.assertIn("Jan 01, 2026", prompt)
        self.assertIn("Jan 05, 2026", prompt)
        self.assertIn("Hiking, Swimming, Running", prompt)
        self.assertIn("Return ONLY the itinerary in the format above", prompt)

# Database Tests

class TestDataBase(unittest.TestCase):

    TEST_DB = "test_tripwise.db"

    # Construct temporary database for testing
    def setUp(self):
        set_database(f"sqlite:///{self.TEST_DB}")
        init_db()

        self.trip = {
            "Destination" : "Tokyo",
            "Start_Date" : date(2026, 1, 1),
            "End_Date" : date(2026, 1, 15),
            "Days" : 14,
            "Budget" : 2500,
            "Traveler_Count" : 1,
            "Traveler_Style" : "Foodie",
            "Interests" : "Car racing"
        }

    # Delete the temporary database
    def tearDown(self):
        if os.path.exists(self.TEST_DB):
            os.remove(self.TEST_DB)

    def test_save_trip(self):
        trip_id = save_trip(
            self.trip["Destination"],
            self.trip["Start_Date"],
            self.trip["End_Date"],
            self.trip["Days"],
            self.trip["Budget"],
            self.trip["Traveler_Count"],
            self.trip["Traveler_Style"],
            self.trip["Interests"]
        )

        trip = get_trip(trip_id)

        self.assertIsNotNone(trip)
        self.assertEqual(trip["Destination"], "Tokyo")
        self.assertEqual(trip["Start_Date"], date(2026, 1, 1))
        self.assertEqual(trip["End_Date"], date(2026, 1, 15))
        self.assertEqual(trip["Days"], 14)
        self.assertEqual(trip["Budget"], 2500)
        self.assertEqual(trip["Traveler_Count"], 1)
        self.assertEqual(trip["Traveler_Style"], "Foodie")
        self.assertEqual(trip["Interests"], "Car racing")

    def test_save_flight(self):
        trip_id = save_trip(
            self.trip["Destination"],
            self.trip["Start_Date"],
            self.trip["End_Date"],
            self.trip["Days"],
            self.trip["Budget"],
            self.trip["Traveler_Count"],
            self.trip["Traveler_Style"],
            self.trip["Interests"]
        )
        flight_id = save_flight(
            trip_id,
            "Cheapest",
            "Delta Airlines",
            350,
            "2h 50m"
        )

        flight = get_flight(flight_id)

        self.assertIsNotNone(flight)
        self.assertEqual(flight["Trip_ID"], trip_id)
        self.assertEqual(flight["Tier"], "Cheapest")
        self.assertEqual(flight["Airline"], "Delta Airlines")
        self.assertEqual(flight["Price"], 350)
        self.assertEqual(flight["Duration"], "2h 50m")

    def test_save_hotel(self):
        trip_id = save_trip(
            self.trip["Destination"],
            self.trip["Start_Date"],
            self.trip["End_Date"],
            self.trip["Days"],
            self.trip["Budget"],
            self.trip["Traveler_Count"],
            self.trip["Traveler_Style"],
            self.trip["Interests"]
        )
        hotel_id = save_hotel(
            trip_id,
            "Cheapest",
            "Mariott Tokyo",
            55.5,
            "7.8/10",
            "Downtown Tokyo"
        )

        hotel = get_hotel(hotel_id)

        self.assertIsNotNone(hotel)
        self.assertEqual(hotel["Trip_ID"], trip_id)
        self.assertEqual(hotel["Name"], "Mariott Tokyo")
        self.assertEqual(hotel["Price_Per_Night"], 55.5)
        self.assertEqual(hotel["Rating"], "7.8/10")
        self.assertEqual(hotel["Location"], "Downtown Tokyo")

    def test_save_activity(self):
        trip_id = save_trip(
            self.trip["Destination"],
            self.trip["Start_Date"],
            self.trip["End_Date"],
            self.trip["Days"],
            self.trip["Budget"],
            self.trip["Traveler_Count"],
            self.trip["Traveler_Style"],
            self.trip["Interests"]
        )
        activity_id = save_activity(
            trip_id,
            "Hiking",
            10,
            "Outdoors",
            "Hike Mount Tokyo"
        )

        activity = get_activity(activity_id)

        self.assertIsNotNone(activity)
        self.assertEqual(activity["Trip_ID"], trip_id)
        self.assertEqual(activity["Name"], "Hiking")
        self.assertEqual(activity["Cost"], 10)
        self.assertEqual(activity["Category"], "Outdoors")
        self.assertEqual(activity["Description"], "Hike Mount Tokyo")

    def test_save_plan(self):
        trip_id = save_trip(
            self.trip["Destination"],
            self.trip["Start_Date"],
            self.trip["End_Date"],
            self.trip["Days"],
            self.trip["Budget"],
            self.trip["Traveler_Count"],
            self.trip["Traveler_Style"],
            self.trip["Interests"]
        )
        flight_id = save_flight(
            trip_id,
            "Cheapest",
            "Delta Airlines",
            350,
            "2h 50m"
        )
        hotel_id = save_hotel(
            trip_id,
            "Cheapest",
            "Mariott Tokyo",
            55.5,
            "7.8/10",
            "Downtown Tokyo"
        )

        flight = get_flight(flight_id)
        hotel = get_hotel(hotel_id)
        trip = get_trip(trip_id)

        base_cost = calculate_base_cost(trip, flight, hotel)
        remaining_budget = trip["Budget"] - base_cost
        plan_id = save_plan(
            trip_id,
            "Cheapest",
            flight_id,
            hotel_id,
            base_cost,
            remaining_budget,
            "Test itinerary text"
        )

        plan = get_plan(plan_id)

        self.assertIsNotNone(plan)
        self.assertEqual(plan["Trip_ID"], trip_id)
        self.assertEqual(plan["Plan_Type"], "Cheapest")
        self.assertEqual(plan["Flight_ID"], flight_id)
        self.assertEqual(plan["Hotel_ID"], hotel_id)
        self.assertEqual(plan["Total_Cost"], base_cost)
        self.assertEqual(plan["Remaining_Budget"], remaining_budget)
        self.assertEqual(plan["Itinerary_Text"], "Test itinerary text")



        
        

    