from datetime import datetime, timezone
from odds_fetcher import Pick


def format_pick(pick: Pick) -> str:
    """Format a single pick for Telegram."""
    prob_pct = round(pick.probability * 100, 1)

    # Parse time
    try:
        dt = datetime.fromisoformat(pick.commence_time.replace("Z", "+00:00"))
        time_str = dt.strftime("%d %b %H:%M UTC")
    except Exception:
        time_str = pick.commence_time

    return (
        f"  ✅ <b>{pick.team}</b>\n"
        f"  📊 {pick.american_odds} / {pick.decimal_odds:.2f}\n"
        f"  🎯 {prob_pct}%\n"
        f"  📖 {pick.bookmaker}\n"
        f"  ⏰ {time_str}"
    )


def format_picks_message(picks: list[Pick]) -> list[str]:
    """Format all picks into Telegram messages (split if too long)."""
    if not picks:
        return ["🟢 <b>GREEN ZONE</b>\n\n❌ Нет пиков с 80%+ вероятностью прямо сейчас.\nСледующее обновление через 4 часа."]

    now = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")
    header = f"🟢 <b>GREEN ZONE PICKS</b>\n📅 {now}\n{'─' * 28}\n\n"

    # Group by league
    by_league: dict[str, list[Pick]] = {}
    for p in picks:
        by_league.setdefault(p.league, []).append(p)

    messages = []
    current = header

    for league, league_picks in by_league.items():
        block = f"<b>{league}</b>\n\n"
        for p in league_picks:
            block += f"🏟 {p.home} vs {p.away}\n"
            block += format_pick(p) + "\n\n"

        # Telegram message limit: 4096 chars
        if len(current) + len(block) > 3800:
            messages.append(current)
            current = f"🟢 <b>GREEN ZONE (продолжение)</b>\n\n{block}"
        else:
            current += block

    if current.strip():
        messages.append(current)

    # Footer
    footer = (
        f"{'─' * 28}\n"
        f"📊 Всего пиков: {len(picks)} | Мин. вероятность: 80%\n"
        f"⚠️ Ставки — это риск. Играйте ответственно."
    )

    if len(messages[-1]) + len(footer) > 3800:
        messages.append(footer)
    else:
        messages[-1] += footer

    return messages
