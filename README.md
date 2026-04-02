# 🟢 GREEN ZONE BOT

Telegram-бот для автоматических пиков на спорт с вероятностью 80%+.
Постит в канал каждые 4 часа. Бесплатный стек.

---

## ПОШАГОВЫЙ ЗАПУСК

### Шаг 1: Получи API ключ The Odds API (бесплатно)

1. Иди на https://the-odds-api.com
2. Зарегистрируйся — бесплатный тир: 500 запросов/мес
3. Скопируй API Key

### Шаг 2: Создай бота в Telegram

1. Открой @BotFather
2. /newbot → имя: Green Zone Picks → username: greenzone_picks_bot (или своё)
3. Скопируй токен

### Шаг 3: Создай Telegram канал

1. Создай канал, например @greenzone_picks
2. Добавь бота как администратора с правом публикации
3. Запомни username канала: @greenzone_picks

### Шаг 4: Деплой на Railway

1. Иди на https://railway.app — залогинься через GitHub
2. New Project → Deploy from GitHub repo
3. Залей этот код в GitHub репозиторий:
   ```
   git init
   git add .
   git commit -m "Green Zone Bot v1"
   git remote add origin https://github.com/YOUR_USER/green-zone-bot.git
   git push -u origin main
   ```
4. В Railway → Variables добавь:
   - BOT_TOKEN = токен от BotFather
   - ODDS_API_KEY = ключ от The Odds API
   - CHANNEL_ID = @greenzone_picks (или -100xxxxx)
5. Deploy → бот запустится автоматически

### Шаг 5: Проверка

1. Напиши боту /start — должен ответить
2. Напиши /post — вручную запустит пики в канал
3. Дальше бот постит автоматически каждые 4 часа

---

## МОНЕТИЗАЦИЯ (следующий шаг)

Когда в канале будут подписчики:
- Приватный канал + Telegram Stars за доступ
- Или два канала: бесплатный (1-2 пика/день) + платный (все пики)

---

## ФАЙЛЫ

- main.py — бот (aiogram 3, scheduler)
- odds_fetcher.py — парсинг The Odds API, фильтр 80%+
- formatter.py — форматирование пиков для Telegram
- config.py — настройки
- Procfile — для Railway
- requirements.txt — зависимости
