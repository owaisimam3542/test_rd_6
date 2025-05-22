from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import requests
# OLLAMA_API_BASE = "https://8000-2401-4900-1c36-7c09-fd83-668d-d6da-7da8.ngrok-free.app"

import json
# import fitz  # For PDF parsing
import re  # For extracting JSON from text

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# Data Models
# -------------------------------
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    history: List[Message]
    name: str
    dob: str
    tob: str
    pob: str
    feature: str
    language: str = "English"


class PastLifeRequest(BaseModel):
    name: str
    dob: str
    tob: str
    pob: str
    language: str = "English"


class MatchRequest(BaseModel):
    name: str
    dob: str
    tob: str
    pob: str
    partner_name: str
    language: str = "English"


class SpiritualHabitsRequest(BaseModel):
    name: str
    dob: str
    tob: str
    pob: str
    language: str = "English"


# -------------------------------
# /chat endpoint
# -------------------------------
@app.post("/chat")
def chat_with_astrologer(data: ChatRequest):
    history_text = "\n".join(
        [f"{msg.role.capitalize()}: {msg.content}" for msg in data.history]
    ).strip()

    is_global_update = (
            data.feature == "🗞️ Astrology + Current Affairs" and
            (not data.history or "current astrological situation" in history_text.lower())
    )

    if is_global_update:
        prompt = f"""
You are a Vedic astrologer AI.

Task: Provide a concise global update on the **current astrological situation** — including planetary transits, retrogrades, eclipses, and significant aspects.

Instructions:
- Respond ONLY in {data.language}.
- Mention major ongoing astrological events (1 per section).
- For each event, follow this format:
  - 🌌 Event Summary (e.g., "Saturn Retrograde in Aquarius")
  - 🔍 What It Means (brief mystical interpretation)
  - 🌱 Suggestions (2–3 short spiritual or lifestyle tips)

Formatting Rules:
- Use only bullet points.
- No long paragraphs or intros.
- Keep each point brief, clear, and engaging.
- Do not add extra context or commentary.
"""
    elif data.feature == "🗞️ Astrology + Current Affairs":
        prompt = f"""
You are a modern Vedic astrologer AI who explains the personal impact of **current astrological events** — based on the user's birth chart.

User's birth details:
Name: {data.name}
DOB: {data.dob}
TOB: {data.tob}
POB: {data.pob}

Conversation:
{history_text}

Instructions:
- Connect the user's chart to ongoing astrological events (e.g., eclipses, retrogrades, transits).
- Use relevant Vedic terms like gochar, dasha, planetary houses.
- Address specific life areas: career, emotions, relationships, health, finances.
- Offer practical or spiritual tips where needed.

Format for each major event:
- 🔭 **Current Event** (e.g., "Mars transiting 7th House")
  - 🔍 **Effect on You**: clear, mystical summary relevant to user's life
  - 🌱 **Tips**: 2–3 short actionable or spiritual recommendations

Formatting Rules:
- Use clean bullet points only.
- Avoid long or generic paragraphs.
- Make it warm, insightful, and personal.
"""
    else:
        prompt = f"""
You are a wise and friendly astrologer providing guidance in the area of {data.feature}.

User's birth details:
Name: {data.name}
Date of Birth: {data.dob}
Time of Birth: {data.tob}
Place of Birth: {data.pob}

Only respond with insights relevant to {data.feature}.
Respond in {data.language} language only.

Conversation so far:
{history_text}

Give helpful and accurate insights related to {data.feature}.

Make your response:
- Concise and easy to understand
- Well-structured using bullet points
- Free of unnecessary repetition
- Friendly and warm in tone
- Start with a short summary (1–2 lines), then give bullet points
"""

    try:
        # http://localhost:11434/api/generate
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })

        reply = response.json().get("response", "Sorry, no reply.")

        return {"reply": reply}

    except Exception as e:
        print("Chat Error:", e)
        return {"reply": "Something went wrong during chat."}


# -------------------------------
# /decode endpoint
# -------------------------------
# @app.post("/decode")
# async def decode_birth_chart(
#     feature: str = Form(...),
#     language: str = Form("English"),
#     file: UploadFile = File(None),
#     name: str = Form(None),
#     dob: str = Form(None),
#     tob: str = Form(None),
#     pob: str = Form(None)
# ):
#     try:
#         if file:
#             contents = await file.read()
#             try:
#                 with fitz.open(stream=contents, filetype="pdf") as doc:
#                     parsed_text = ""
#                     for page in doc:
#                         parsed_text += page.get_text()
#
#                 input_data = f"""
# The user has uploaded a Kundli (birth chart) PDF. Below is the extracted content:
#
# {parsed_text}
#
# Use this data to decode their Vedic birth chart.
# """
#             except Exception as e:
#                 print("PDF parsing error:", e)
#                 input_data = "Kundli PDF was uploaded but could not be parsed. Proceed with general chart decoding."
#         else:
#             input_data = f"""
# Name: {name}
# DOB: {dob}
# TOB: {tob}
# POB: {pob}
# """
#
#         prompt = f"""
# You are a professional Vedic astrologer AI decoder.
#
# Task: Decode the live birth chart of the user.
#
# Data provided:
# {input_data}
#
# Respond ONLY in {language}.
# Explain clearly:
# - Houses, Doshas, and Yogas in user's chart
# - Real-time planetary transits and their impact
# - Answer: "What's happening in my life now?"
#
# Make your answer:
# - Concise but insightful
# - Structured in bullet points
# - Friendly and understandable
# """
#
#         response = requests.post("http://localhost:11434/api/generate", json={
#             "model": "mistral",
#             "prompt": prompt,
#             "stream": False
#         })
#
#         reply = response.json().get("response", "Unable to decode chart.")
#         return JSONResponse(content={"reply": reply})
#
#     except Exception as e:
#         print("Decode Error:", e)
#         return JSONResponse(content={"reply": "Something went wrong while decoding."})

# -------------------------------
# /past-life endpoint
# -------------------------------
@app.post("/past-life")
def past_life_reading(data: PastLifeRequest):
    prompt = f"""
You are a mystical karmic astrologer AI that reveals past life stories using Vedic astrology principles.

User's Birth Info:
Name: {data.name}
DOB: {data.dob}
TOB: {data.tob}
POB: {data.pob}

Instructions:
- Analyze the user's past life karma based on retrograde planets, Rahu, Ketu, and planetary houses.
- Create a visual storyline in 2 to 4 "comic panels" format.
- Each panel should be a short narrative (2–3 sentences max).
- Format the response as a list of panels, with optional suggested image themes.
- Use only {data.language} language.
- Be warm, spiritual, and engaging — like a wise rishi sharing insights.

Respond in this JSON format:
[
  {{ "text": "Short narration for panel 1", "image": "Optional prompt like 'A monk meditating under stars'" }},
  ...
]
"""

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })

        raw_text = response.json().get("response", "[]")

        try:
            panels = json.loads(raw_text)
        except Exception:
            panels = [{"text": raw_text}]

        return {"panels": panels}

    except Exception as e:
        print("Past Life Error:", e)
        return JSONResponse(content={"panels": [{"text": "Something went wrong while generating past life reading."}]})


# -------------------------------
# /match endpoint (Updated for JSON parsing)
# -------------------------------
@app.post("/match")
def match_compatibility(data: MatchRequest):
    prompt = f"""
You are a professional Vedic astrologer AI specialized in relationship compatibility analysis.

User Details:
- Name: {data.name}
- DOB: {data.dob}
- TOB: {data.tob}
- POB: {data.pob}

Partner Name: {data.partner_name}

Respond in {data.language}.

Instructions:
- Calculate overall compatibility (e.g., Guna Milan or synastry principles)
- Output:
  - Love Score (1–100)
  - Conflict Potential (brief)
  - 2–3 Lucky Dates for bonding
  - A short dating tip based on astrology
  - A friendly summary of their love compatibility

Format:
{{
  "love_score": "value",
  "conflict_potential": "short description",
  "lucky_dates": "comma-separated dates",
  "dating_tip": "short advice",
  "summary": "brief relationship analysis"
}}
"""

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })

        raw = response.json().get("response", "{}")

        # Extract JSON block from text
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            json_part = match.group(0)
            data = json.loads(json_part)
        else:
            raise ValueError("No valid JSON found.")

        return JSONResponse(content=data)

    except Exception as e:
        print("Match Compatibility Error:", e)
        return JSONResponse(content={
            "love_score": "N/A",
            "conflict_potential": "Unable to calculate.",
            "lucky_dates": "N/A",
            "dating_tip": "N/A",
            "summary": raw if 'raw' in locals() else "Something went wrong while analyzing compatibility."
        })


# -------------------------------
# /spiritual-habits endpoint
# -------------------------------
# @app.post("/spiritual-habits")
# def spiritual_habit_tracker(data: SpiritualHabitsRequest):
#     prompt = f"""
# You are a spiritual astrologer AI who recommends personalized daily practices based on Vedic astrology.
#
# User Birth Info:
# - Name: {data.name}
# - DOB: {data.dob}
# - TOB: {data.tob}
# - POB: {data.pob}
#
# Respond ONLY in {data.language}.
#
# Instructions:
# - Suggest 3 to 5 personalized spiritual habits.
# - Format response as a JSON list, like:
#   ["Chant 'Om Namah Shivaya'", "Meditate at sunrise", "Fast on Mondays"]
# """
#
#     try:
#         response = requests.post("http://localhost:11434/api/generate", json={
#             "model": "mistral",
#             "prompt": prompt,
#             "stream": False
#         })
#
#         raw = response.json().get("response", "[]")
#         print("🧘 RAW SPIRITUAL HABITS OUTPUT:", raw)
#
#         # Try parsing as list first
#         try:
#             parsed = json.loads(raw)
#             if isinstance(parsed, dict):
#                 habits = list(parsed.values())  # Convert dict to list
#             elif isinstance(parsed, list):
#                 habits = parsed
#             else:
#                 raise ValueError("Parsed output is neither list nor dict")
#         except Exception:
#             # Try regex fallback
#             match = re.search(r'\[(.*?)\]', raw, re.DOTALL)
#             if match:
#                 habits_json = "[" + match.group(1).strip() + "]"
#                 habits = json.loads(habits_json)
#             else:
#                 habits = [raw.strip()]
#
#         return JSONResponse(content={"habits": habits})
#
#     except Exception as e:
#         print("Spiritual Habits Error:", e)
#         return JSONResponse(content={"habits": ["Something went wrong while generating habits."]})
@app.post("/spiritual-habits")
def spiritual_habit_tracker(data: SpiritualHabitsRequest):
    prompt = f"""
    Suggest 5 spiritual daily habits for a person based on their birth details:

    Name: {data.name}
    Date of Birth: {data.dob}
    Time of Birth: {data.tob}
    Place of Birth: {data.pob}

    Respond only in {data.language}.
    Only output a list — one habit per line. Do not explain or add extra context.
    """

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })

        raw = response.json().get("response", "[]")
        print("🧘 RAW SPIRITUAL HABITS OUTPUT:", raw)

        habits = []

        # Try proper JSON parsing first
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                habits = parsed
            elif isinstance(parsed, dict):
                habits = list(parsed.values())
            else:
                raise ValueError("Not a JSON list")
        except Exception:
            # Fallback: extract lines manually
            lines = [line.strip("•- \n\t0123456789.") for line in raw.strip().split("\n") if line.strip()]
            habits = [line for line in lines if len(line) > 3]

        return JSONResponse(content={"habits": habits})

    except Exception as e:
        print("Spiritual Habits Error:", e)
        return JSONResponse(content={"habits": ["कुछ गलत हो गया आध्यात्मिक दिनचर्या निकालते समय।"]})


@app.post("/generate-kundli")
def generate_kundli(data: PastLifeRequest):
    prompt = f"""
You are a Vedic astrologer AI assistant.

User Details:
- Name: {data.name}
- DOB: {data.dob}
- TOB: {data.tob}
- POB: {data.pob}

Goal: Output structured Kundli data as JSON in the format below.

Structure:
{{
  "birth_details": {{
    "name": "...",
    "dob": "...",
    "tob": "...",
    "pob": "...",
    "lagna": "...",
    "rasi": "...",
    "nakshatra": "..."
  }},
  "planetary_positions": [
    {{ "planet": "Sun", "sign": "Taurus", "degree": "04-21-28", "nakshatra": "Krittika", "pada": 3 }},
    ...
  ],
  "charts": {{
    "lagna_chart": ["Sun in 10H Taurus", "Moon in 6H Capricorn", ...],
    "navamsha_chart": ["Sun in Pisces", "Moon in Scorpio", ...]
  }},
  "dashas": {{
    "vimshottari": [
      {{ "period": "MON", "start": "19/05/2025", "end": "23/04/2028" }},
      ...
    ]
  }},
  "yogas": ["Gajakesari Yoga", "Kaal Sarp Dosha"],
  "ashtakvarga": {{
    "sun": [3, 3, 5, 2, 4, 3, 5, 5, 3, 5, 5, 5],
    "moon": [3, 5, 5, 5, 3, 3, 4, 5, 4, 6, 2, 4],
    "total": [27, 30, 31, 21, 29, 23, 26, 33, 25, 36, 26, 30]
  }},
  "shadbala": {{
    "sun": 647.06,
    "moon": 381.66,
    "mars": 318.45,
    "mercury": 391.23,
    "jupiter": 493.2,
    "venus": 465.11,
    "saturn": 268.7
  }}
}}

Only respond in JSON. No explanation, no intro text.
"""

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })

        raw = response.json().get("response", "{}")
        print("🔍 RAW RESPONSE:\n", raw)

        # Extract only the JSON-looking portion
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            clean_json = match.group(0)

            # Remove any trailing commas or "..." manually
            clean_json = re.sub(r',\s*[\.\s]*\.\.\.', '', clean_json)
            clean_json = re.sub(r'\.\.\.', 'null', clean_json)  # Replace ellipsis safely
            clean_json = re.sub(r',\s*}', '}', clean_json)  # Remove trailing commas before braces
            clean_json = re.sub(r',\s*]', ']', clean_json)  # Remove trailing commas before array ends

            structured = json.loads(clean_json)
            return JSONResponse(content=structured)
        else:
            raise ValueError("Structured JSON not detected.")

    except Exception as e:
        print("❌ Kundli Gen Error:", e)
        return JSONResponse(content={"error": "Failed to generate structured Kundli."})
# placeholder, please re-upload main.py
# placeholder, please re-upload main.py