# Disare - AI-Powered Mental Health Mini App

Disare is a premium Telegram Mini App designed for entrepreneurs and busy professionals 25+ to reduce stress, improve sleep, nutrition, and mental health using AI and CBT practices.

## Features

- Telegram Authentication
- AI Chat with personalized recommendations
- Mood Tracker with emotional analysis
- Sleep and Nutrition Journal
- CBT Practices
- Smart Notifications

## Tech Stack

- Backend: Python + FastAPI
- Frontend: Telegram Mini App (HTML/CSS/JS)
- Database: SQLite (development) / Supabase (production)
- AI: OpenRouter API, HuggingFace API
- Hosting: Render/Railway

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   OPENROUTER_API_KEY=your_openrouter_key
   HUGGINGFACE_API_KEY=your_huggingface_key
   ```
5. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

```
disare/
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── mood.py
│   │   └── journal.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── models.py
│   │   └── database.py
│   ├── services/
│   │   ├── ai.py
│   │   └── notifications.py
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/
├── .env
├── requirements.txt
└── README.md
```

## Development

1. Backend API endpoints are documented at `/docs` when running the server
2. Frontend development can be done using the Telegram WebApp API
3. Database migrations are handled through SQLAlchemy

## License

MIT 