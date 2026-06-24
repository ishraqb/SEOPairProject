# TripWise

**TripWise** is a command-line trip planning tool that generates three personalized travel plans — Cheapest, Balanced, and Experience-Focused — tailored to your travel style, interests, and budget. No more jumping between dozens of websites to plan a trip.

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

```
git clone https://github.com/ishraqb/SEOPairProject.git
cd SEOPairProject
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Create a `.env` file in the project root (use `.env.example` as a template):

```
RAPIDAPI_KEY=your_rapidapi_key_here
GEMINI_API_KEY=your_gemini_key_here
```

## Usage

```
python main.py --origin JFK --destination London --start 2026-08-01 --end 2026-08-05 --budget 3000 --travelers 1 --style foodie --interests food,culture,art
```

View past trips:

```
python main.py --history
```

### Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--origin` | Departure airport code | `JFK` |
| `--destination` | Destination city | `London` |
| `--start` | Departure date (YYYY-MM-DD) | `2026-08-01` |
| `--end` | Return date (YYYY-MM-DD) | `2026-08-05` |
| `--budget` | Total budget in USD | `3000` |
| `--travelers` | Number of travelers | `1` |
| `--style` | Your travel style — shapes every plan and activity recommendation | `foodie`, `adventure`, `relaxed` |
| `--interests` | Ranked interests, highest to lowest priority | `food,culture,art` |
| `--history` | View all past trips | — |

## Team

- Ishraq Basher — flights.py, hotels.py, main.py, CI setup
- Yahir Flores — gemini.py, db.py, test_app.py
