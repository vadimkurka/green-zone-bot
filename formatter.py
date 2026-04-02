from datetime import datetime, timezone
from odds_fetcher import Pick


def format_top_picks(picks: list[Pick]) -> str:
    """Top 5 picks - the main daily post."""
    quality_picks = [p for p in picks if p.decimal_odds >= 1.08]
    top = quality_picks[:5] if len(quality_picks) >= 5 else quality_picks

    if not top:
        return ""

    now = datetime.now(timezone.utc).strftime("%d %b %Y").upper()
    lines = [f"<b>TOP {len(top)} GREEN ZONE PICKS — {now}</b>\n"]

    for i, p in enumerate(top, 1):
        prob_pct = round(p.probability * 100, 1)
        try:
            dt = datetime.fromisoformat(p.commence_time.replace("Z", "+00:00"))
            time_str = dt.strftime("%d %b %H:%M UTC")
        except Exception:
            time_str = p.commence_time

        lines.append(
            f"{i}. {p.league} | {p.home} vs {p.away}\n"
            f"   Pick: <b>{p.team}</b>\n"
            f"   Odds: {p.decimal_odds:.2f} | Confidence: {prob_pct}%\n"
            f"   {p.bookmaker} | {time_str}\n"
        )

    lines.append("Betting involves risk. Gamble responsibly.")
    return "\n".join(lines)


def format_picks_message(picks: list[Pick]) -> list[str]:
    messages = []

    # First message: Top picks
    top_msg = format_top_picks(picks)
    if top_msg:
        messages.append(top_msg)

    if not picks:
        messages.append("GREEN ZONE\n\nNo picks above 80% right now.\nNext update in 4 hours.")
        return messages

    # Full board
    now = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    header = f"<b>FULL GREEN ZONE BOARD — {now}</b>\n\n"

    by_league: dict[str, list[Pick]] = {}
    for p in picks:
        by_league.setdefault(p.league, []).append(p)

    current = header

    for league, league_picks in by_league.items():
        block = f"<b>{league}</b>\n\n"
        for p in league_picks:
            prob_pct = round(p.probability * 100, 1)
            try:
                dt = datetime.fromisoformat(p.commence_time.replace("Z", "+00:00"))
                time_str = dt.strftime("%d %b %H:%M UTC")
            except Exception:
                time_str = p.commence_time

            block += (
                f"{p.home} vs {p.away}\n"
                f"Pick: <b>{p.team}</b>\n"
                f"Odds: {p.decimal_odds:.2f} | Confidence: {prob_pct}% | {p.bookmaker}\n"
                f"{time_str}\n\n"
            )

        if len(current) + len(block) > 3800:
            messages.append(current)
            current = f"<b>GREEN ZONE BOARD (cont.)</b>\n\n{block}"
        else:
            current += block

    if current.strip():
        messages.append(current)

    # Footer
    low = round(min(p.probability for p in picks) * 100, 1)
    high = round(max(p.probability for p in picks) * 100, 1)
    footer = f"{len(picks)} picks posted | Confidence range: {low}%–{high}%"

    if len(messages[-1]) + len(footer) + 2 > 3800:
        messages.append(footer)
    else:
        messages[-1] += f"\n{footer}"

    return messages
