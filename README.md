# TripWise

**TripWise** is a command-line trip planning tool that generates three personalized travel plans — Cheapest, Balanced, and Experience-Focused — tailored to your travel style, interests, and budget. No more jumping between 38 websites to plan a trip.

## What makes TripWise different

Most travel tools show you flights or hotels in isolation. TripWise is built around **you** — your travel style, your ranked interests, and your budget. Tell TripWise you're a foodie who prioritizes local cuisine over sightseeing, and every plan it generates reflects that. An adventurer gets a completely different set of recommendations for the same destination.

Three plans, one command — each one adapted to how you actually want to travel:
- **$ Cheapest** — budget-friendly options, free and low-cost activities
- **$$ Balanced** — mid-range flights and hotels, mix of paid and free experiences
- **$$$ Experience-Focused** — business class flights, upscale hotels, premium activities

## What it does

- Searches for real flights (economy and business class) using the Booking.com API
- Searches for real hotel options using the Booking.com API
- Generates three complete day-by-day itineraries using Google Gemini AI, personalized to your travel style and interests
- Saves your trip and all three plans to a local database
- Lets you view past trips with `--history`

## APIs Used

- [Booking.com via RapidAPI](https://rapidapi.com/booking-com15/api/booking-com15) — flights and hotels
- [Google Gemini](https://aistudio.google.com/) — AI itinerary generation

## Setup

1. Clone the repo:
