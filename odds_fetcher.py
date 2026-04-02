import aiohttp
import logging
from dataclasses import dataclass
from config import ODDS_API_KEY, ODDS_API_URL, REGIONS, MARKETS, ODDS_FORMAT, MIN_PROBABILITY

logger = logging.getLogger(__name__)


@dataclass
class Pick:
    sport: str
    league: str
    home: str
    away: str
    team: str
    decimal_odds: float
    american_odds: str
    probability: float
    commence_time: str
    bookmaker: str


def decimal_to_american(decimal_odds: float) -> str:
    if decimal_odds >= 2.0:
        american = round((decimal_odds - 1) * 100)
        return f"+{american}"
    else:
        american = round(-100 / (decimal_odds - 1))
        return f"{american}"


def implied_prob(decimal_odds: float) -> float:
    return 1 / decimal_odds if decimal_odds > 0 else 0


SPORT_KEYS = [
    "americanfootball_nfl",
    "americanfootball_ncaaf",
    "basketball_nba",
    "basketball_ncaab",
    "baseball_mlb",
    "icehockey_nhl",
    "soccer_usa_mls",
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_uefa_champs_league",
    "mma_mixed_martial_arts",
    "tennis_atp_french_open",
    "tennis_wta_french_open",
    "tennis_atp_aus_open",
    "tennis_wta_aus_open",
    "tennis_atp_wimbledon",
    "tennis_wta_wimbledon",
    "tennis_atp_us_open",
    "tennis_wta_us_open",
]

SPORT_NAMES = {
    "americanfootball_nfl": "🏈 NFL",
    "americanfootball_ncaaf": "🏈 NCAAF",
    "basketball_nba": "🏀 NBA",
    "basketball_ncaab": "🏀 NCAAB",
    "baseball_mlb": "⚾ MLB",
    "icehockey_nhl": "🏒 NHL",
    "soccer_usa_mls": "⚽ MLS",
    "soccer_epl": "⚽ EPL",
    "soccer_spain_la_liga": "⚽ La Liga",
    "soccer_germany_bundesliga": "⚽ Bundesliga",
    "soccer_italy_serie_a": "⚽ Serie A",
    "soccer_france_ligue_one": "⚽ Ligue 1",
    "soccer_uefa_champs_league": "⚽ UCL",
    "mma_mixed_martial_arts": "🥊 MMA",
}


async def fetch_sports() -> list[str]:
    url = f"{ODDS_API_URL}/?apiKey={ODDS_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                logger.error(f"Sports API error: {resp.status}")
                return []
            data = await resp.json()
            active = [s["key"] for s in data if not s.get("has_outrights", False)]
            return [k for k in active if k in SPORT_KEYS]


async def fetch_odds(sport_key: str) -> list[dict]:
    url = (
        f"{ODDS_API_URL}/{sport_key}/odds/"
        f"?apiKey={ODDS_API_KEY}"
        f"&regions={REGIONS}"
        f"&markets={MARKETS}"
        f"&oddsFormat={ODDS_FORMAT}"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                logger.error(f"Odds API error for {sport_key}: {resp.status}")
                return []
            remaining = resp.headers.get("x-requests-remaining", "?")
            logger.info(f"API requests remaining: {remaining}")
            return await resp.json()


def extract_picks(events: list[dict], sport_key: str) -> list[Pick]:
    picks = []

    for event in events:
        home = event.get("home_team", "")
        away = event.get("away_team", "")
        commence = event.get("commence_time", "")

        for bookmaker in event.get("bookmakers", []):
            book_name = bookmaker.get("title", "")

            for market in bookmaker.get("markets", []):
                if market.get("key") != "h2h":
                    continue

                for outcome in market.get("outcomes", []):
                    team = outcome.get("name", "")
                    price = outcome.get("price", 0)

                    if price <= 0:
                        continue

                    # Skip draws — not actionable for Green Zone
                    if team == "Draw":
                        continue

                    prob = implied_prob(price)

                    if prob >= MIN_PROBABILITY:
                        picks.append(Pick(
                            sport=sport_key,
                            league=SPORT_NAMES.get(sport_key, sport_key),
                            home=home,
                            away=away,
                            team=team,
                            decimal_odds=price,
                            american_odds=decimal_to_american(price),
                            probability=prob,
                            commence_time=commence,
                            bookmaker=book_name,
                        ))

    return picks


def deduplicate_picks(picks: list[Pick]) -> list[Pick]:
    """Keep ONE best pick per match — highest probability favorite."""
    best = {}
    for p in picks:
        # One pick per match
        key = f"{p.home}_{p.away}"
        if key not in best or p.probability > best[key].probability:
            best[key] = p
    return sorted(best.values(), key=lambda x: x.probability, reverse=True)


async def get_green_zone_picks() -> list[Pick]:
    active_sports = await fetch_sports()
    logger.info(f"Active sports: {len(active_sports)}")

    all_picks = []
    for sport_key in active_sports:
        events = await fetch_odds(sport_key)
        picks = extract_picks(events, sport_key)
        all_picks.extend(picks)
        logger.info(f"{sport_key}: {len(events)} events, {len(picks)} green picks")

    return deduplicate_picks(all_picks)
