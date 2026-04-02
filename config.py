import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")  # @your_channel or -100xxxxx

# Green Zone: only 80%+ implied probability
MIN_PROBABILITY = 0.80

# Odds API settings
ODDS_API_URL = "https://api.the-odds-api.com/v4/sports"
REGIONS = "us,eu"
MARKETS = "h2h"
ODDS_FORMAT = "decimal"

# Fetch interval in seconds (every 4 hours = saves API quota)
FETCH_INTERVAL = 14400
