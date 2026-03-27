import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Load the keys from your .env file
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# 2. Establish the connection to the cloud
supabase: Client = create_client(url, key)

def save_user_profile(user_name, user_gender, bot_name):
    """Saves the user's setup choices to the 'profiles' table."""
    data = {
        "user_name": user_name,
        "user_gender": user_gender,
        "bot_name": bot_name
    }
    # This sends the data to the table you just created in the dashboard
    result = supabase.table("profiles").insert(data).execute()
    return result.data[0]

def save_chat_message(profile_id, sender, content):
    """Saves a message (from either User or Bot) to the 'messages' table."""
    data = {
        "profile_id": profile_id,
        "sender": sender,
        "content": content
    }
    supabase.table("messages").insert(data).execute()

def get_chat_history(profile_id):
    """Fetches past messages so the AI remembers the conversation."""
    result = supabase.table("messages").select("*").eq("profile_id", profile_id).order("created_at").execute()
    return result.data