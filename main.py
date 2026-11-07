import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from google import genai
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Load environment variables explicitly from current directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY is not set! Check your .env file.")

client = genai.Client(api_key=API_KEY) if API_KEY else None

app = FastAPI(
    title="AI Email Generator Pro",
    description="Professional AI-powered email drafting engine."
)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "email": None,
            "recipient_name": "",
            "sender_name": "",
            "purpose": "",
            "tone": "Professional",
            "email_date": ""
        }
    )


@app.post("/generate")
async def generate_email(
    request: Request,
    recipient_name: str = Form(...),
    sender_name: Optional[str] = Form(""),
    purpose: str = Form(...),
    tone: str = Form("Professional"),
    email_date: Optional[str] = Form("")
):
    try:
        if not client:
            raise ValueError("GEMINI_API_KEY is missing or invalid. Check your .env file.")

        sender_instruction = f"Sender Name / Signature: {sender_name}" if sender_name else "Do not include a specific sender name unless customary."
        date_instruction = f"Relevant Date to mention: {email_date}" if email_date else "No specific date required."

        prompt = f"""
You are an expert executive communication assistant.

Draft a complete, polished email based on these inputs:
- Recipient Name: {recipient_name}
- Email Purpose: {purpose}
- Desired Tone: {tone}
- {date_instruction}
- {sender_instruction}

Guidelines:
1. Start with an explicit, professional "Subject: [Your Subject Line]" line at the top. DO NOT include your own name or sender name inside the subject line. Keep the subject line concise and strictly about the email's purpose.
2. Follow with a clean line break and an appropriate greeting.
3. Write well-structured paragraphs aligned strictly with the specified tone.
4. Conclude with a natural closing and place the sender name ({sender_name}) strictly at the bottom signature block if provided.
5. Output ONLY the raw subject line and email body. No extra intros or conversational commentary.
"""

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        generated_email = response.text.strip()

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "email": generated_email,
                "recipient_name": recipient_name,
                "sender_name": sender_name,
                "purpose": purpose,
                "tone": tone,
                "email_date": email_date
            }
        )

    except Exception as e:
        print("GEMINI GENERATION ERROR:", str(e))
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"Failed to generate email: {str(e)}",
                "email": None,
                "recipient_name": recipient_name,
                "sender_name": sender_name,
                "purpose": purpose,
                "tone": tone,
                "email_date": email_date
            }
        )