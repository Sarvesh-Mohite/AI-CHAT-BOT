# 🤖 AI Friend - Persona-Based Chat & Scene Generation

A modern, full-stack AI companion application featuring dynamic personas, persistent memory, and automated scene generation. This project utilizes a multi-model pipeline via OpenRouter to provide high-quality chat and visual experiences using 2026's leading open-source models.

## ✨ Features

- **Dynamic Personas:** Choose between different AI personalities (e.g., Maya or Leo) with unique conversational styles.
- **AI Scene Generation:** A "Generate Scene" feature that uses a dedicated "Prompt Expander" model to transform chat context into rich visual prompts for image generation.
- **Persistent Memory:** Integrated with **Supabase** to store user profiles, chat history, and generated images.
- **High-Traffic Resilience:** Built-in error handling with "Retry" logic to manage API rate limits gracefully.
- **Real-time UI:** Clean, dark-mode interface with "thinking" indicators and instant message updates.

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | Vanilla JavaScript, Tailwind CSS, HTML5 |
| **Backend** | Python 3.10+, FastAPI, Uvicorn |
| **Database** | Supabase (PostgreSQL) |
| **LLM Gateway** | OpenRouter API |
| **Models (2026)** | `stepfun/step-3.5-flash:free` (Chat), `meta-llama/llama-3.2-3b-instruct:free` (Prompt Expansion), `black-forest-labs/flux-1-lite:free` (Images) |

## 🚀 Getting Started

### 1. Prerequisites
- Python installed on your machine.
- A [Supabase](https://supabase.com/) account and project.
- An [OpenRouter](https://openrouter.ai/) API key.

### 2. Environment Setup
Create a `.env` file in your root directory:
```env
OPENROUTER_API_KEY=your_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Database Configuration
Run the following SQL in your Supabase SQL Editor to set up the required tables:
```sql
-- Profiles table
create table profiles (
  id uuid default gen_random_uuid() primary key,
  user_name text,
  user_gender text,
  bot_name text,
  created_at timestamp with time zone default now()
);

-- Chat messages table
create table messages (
  id uuid default gen_random_uuid() primary key,
  profile_id uuid references profiles(id),
  sender text,
  content text,
  created_at timestamp with time zone default now()
);

-- Image generation table
create table image_chats (
  id uuid default gen_random_uuid() primary key,
  profile_id uuid references profiles(id),
  trigger_message text,
  image_url text,
  created_at timestamp with time zone default now()
);
```

### 4. Installation & Run
```bash
# Install dependencies
pip install fastapi uvicorn openai python-dotenv supabase

# Start the backend server
python -m uvicorn main:app --reload
```
Open `index.html` in your browser to start chatting!

## 📸 Preview
*Insert a screenshot or GIF of your app here to show off that clean Tailwind UI!*

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.

---
Built by [Sarvesh Mohite]
```
