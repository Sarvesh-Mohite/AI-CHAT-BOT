# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import time

# Import your custom modules
from personas import get_persona, get_image_prompt_persona # Import the new persona
from database import save_user_profile, save_chat_message, supabase

load_dotenv()

# Initialize OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class ProfileCreate(BaseModel):
    user_name: str
    user_gender: str
    bot_name: str

class ChatMessage(BaseModel):
    profile_id: str
    user_message: str

# Model for the image request
class ImageRequest(BaseModel):
    profile_id: str
    bot_reply: str

# Endpoint 1: Create a Profile
@app.post("/create-profile")
async def create_profile(profile: ProfileCreate):
    try:
        new_profile = save_user_profile(profile.user_name, profile.user_gender, profile.bot_name)
        return {"status": "success", "profile": new_profile}
    except Exception as e:
        print(f"Profile Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create profile")

# Endpoint 2: Chat with the Bot
@app.post("/chat")
async def chat(chat_data: ChatMessage):
    try:
        profile_res = supabase.table("profiles").select("*").eq("id", chat_data.profile_id).execute()
        if not profile_res.data:
            return {"bot_reply": "Profile session expired. Please refresh."}
            
        user_profile = profile_res.data[0]
        
        # Determine persona based on the bot_gender (stored in user_gender column)
        system_prompt = get_persona(user_profile['user_gender'], user_profile['bot_name'])

        # 2. Call Dolphin 2.9 (or Llama 3.3-70B-Instruct:free for 2026)
        response = client.chat.completions.create(
            # Switch back to your Dolphin ID when credits allow
            model="stepfun/step-3.5-flash:free", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chat_data.user_message},
            ]
        )
        
        bot_reply = response.choices[0].message.content

        # 3. Save to Supabase
        save_chat_message(chat_data.profile_id, "user", chat_data.user_message)
        save_chat_message(chat_data.profile_id, "bot", bot_reply)

        return {"bot_reply": bot_reply}

    except Exception as e:
        print(f"AI Error: {e}")
        return {"bot_reply": "The AI is feeling a bit sleepy right now. Could you try saying that again?"}
    
    except Exception as e:
        print(f"AI Error: {e}")
        # Raising a 503 tells the frontend the service is temporarily busy
        raise HTTPException(status_code=503, detail="AI Service Busy")

# Endpoint 3: Generate a Scene Image (New for 2026!)
@app.post("/generate-image")
async def generate_image(image_data: ImageRequest):
    try:
        # 1. Fetch Profile info (to get bot_name)
        profile_res = supabase.table("profiles").select("*").eq("id", image_data.profile_id).execute()
        user_profile = profile_res.data[0]
        bot_name = user_profile['bot_name']

        # 2. Translate Bot Reply into an Image Prompt (using a free text model)
        prompt_persona = get_image_prompt_persona(image_data.bot_reply, bot_name)
        
        prompt_response = client.chat.completions.create(
            model="google/gemma-3-27b-it:free", # Fast/Free for prompt translation
            messages=[{"role": "user", "content": prompt_persona}],
            temperature=0.5
        )
        expanded_prompt = prompt_response.choices[0].message.content
        print(f"Expanded Prompt: {expanded_prompt}") # Debug

        # 3. Call a FREE Image model on OpenRouter
        image_response = client.chat.completions.create(
            # Good FREE 2026 Image Models:
            # - 'fofr/stable-diffusion-3:free'
            # - 'black-forest-labs/flux-1-lite:free'
            model="black-forest-labs/flux-1-lite:free", 
            messages=[{"role": "user", "content": expanded_prompt}],
            stream=False,
            # For 2026, OpenRouter often returns URLs in the content or as a tool call
            extra_body={"response_format": {"type": "image_url"}} # New for 2026 format
        )
        
        # 2026 response format check
        image_url = image_response.choices[0].message.content.strip()

        if not image_url.startswith("http"):
            # Some free providers place the URL in content as text.
            image_url = image_response.choices[0].message.content
        
        # 4. Save to Supabase
        supabase.table("image_chats").insert({
            "profile_id": image_data.profile_id,
            "trigger_message": image_data.bot_reply,
            "image_url": image_url
        }).execute()

        return {"image_url": image_url}

    except Exception as e:
        print(f"Image Error: {e}")
        return {"image_url": "https://via.placeholder.com/300x300.png?text=Image+Generation+Error"}
    
    except Exception as e:
        print(f"Image Error: {e}")
        raise HTTPException(status_code=503, detail="Image Service Busy")