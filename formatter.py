from datetime import datetime, timezone
from odds_fetcher import Pick


def format_pick_clean(pick: Pick) -> str:
    prob_pct = round(pick.probability * 100, 1)

    try:
        dt = datetime.fromisoformat(pick.commence_time.replace("Z", "+00:00"))
        time_str = dt.strftime("%d %b %H:%M UTC")
    except Exception:
        time_str = pick.commence_time

    return (
        f"{pick.home} vs {pick.away}\n"
        f"Pick: <b>{pick.team}</b>\n"
        f"Odds: {pick.american_odds} / {pick.decimal_odds:.2f} | "
        f"Confidence: {prob_pct}% | {pick.bookmaker}\n"
        f"{time_str}"
    )


def format_top_picks(picks: list[Pick]) -> str:
    """Top 5 picks - the premium daily post."""
    # Filter out ultra-low odds (1.01-1.06) and take top 5 by probability
    quality_picks = [p for p in picks if p.decimal_odds >= 1.08]
    top = quality_picks[:5] if len(quality_picks) >= 5 else quality_picks

    if not top:
        return ""

    now = datetime.now(timezone.utc).strftime("%d %b %Y")
    lines = [f"<b>TOP {len(top)} GREEN ZONE PICKS — {now}</b>\n"]

    for i, p in enumerate(top, 1):
        prob_pct = round(p.probability * 100, 1)
        try:
            dt = datetime.fromisoformat(p.commence_time.replace("Z", "+00:00"))
            time_str = dt.strftime("%d %b %H:%M UTC")
        except Exception:
            time_str = p.commence_time

        lines.append(
            f"{i}. {p.league}\n"
            f"   {p.home} vs {p.away}\n"
            f"   Pick: <b>{p.team}</b>\n"
            f"   Odds: {p.american_odds} / {p.decimal_odds:.2f} | {prob_pct}%\n"
            f"   {p.bookmaker} | {time_str}\n"
        )

    lines.append("Betting involves risk. Gamble responsibly.")
    return "\n".join(lines)


def format_picks_message(picks: list[Pick]) -> list[str]:
    messages = []

    # First message: Top picks (the main value post)
    top_msg = format_top_picks(picks)
    if top_msg:
        messages.append(top_msg)

    # Second message: Full list for those who want everything
    if not picks:
        messages.append("GREEN ZONE\n\nNo picks with 80%+ probability right now.\nNext update in 4 hours.")
        return messages

    now = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    header = f"<b>ALL GREEN ZONE PICKS</b> — {now}\n{'─' * 30}\n\n"

    by_league: dict[str, list[Pick]] = {}
    for p in picks:
        by_league.setdefault(p.league, []).append(p)

    current = header

    for league, league_picks in by_league.items():
        block = f"<b>{league}</b>\n\n"
        for p in league_picks:
            block += format_pick_clean(p) + "\n\n"

        if len(current) + len(block) > 3800:
            messages.append(current)
            current = f"<b>GREEN ZONE (cont.)</b>\n\n{block}"
        else:
            current += block

    if current.strip():
        messages.append(current)

    footer = f"{'─' * 30}\nTotal: {len(picks)} picks | Min probability: 80%"

    if len(messages[-1]) + len(footer) > 3800:
        messages.append(footer)
    else:
        messages[-1] += footer

    return messages
