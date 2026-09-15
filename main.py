import os

from dotenv import load_dotenv
from google import genai

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


# Load environment variables
load_dotenv()


# Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


# FastAPI App
app = FastAPI(title="AI Email Generator")


# Templates
templates = Jinja2Templates(directory="templates")


# Static files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# Home Page
@app.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "email": None,
            "recipient_name": "",
            "purpose": "",
            "tone": ""
        }
    )


# Generate Email
@app.post("/generate")
def generate_email(
    request: Request,
    recipient_name: str = Form(...),
    purpose: str = Form(...),
    tone: str = Form(...)
):

    prompt = f"""
You are an AI email writing assistant.

Generate a complete email using the following information:

Recipient Name: {recipient_name}
Email Purpose: {purpose}
Tone: {tone}

Instructions:
- Create a suitable subject line.
- Write a complete email.
- Use the selected tone.
- Keep the email clear, natural and professional.
- Include an appropriate greeting.
- Include a suitable closing.
- Do not explain the email.
- Return only the generated email.
"""


    # Gemini response
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )


    generated_email = response.text


    # Return result to HTML
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "email": generated_email,
            "recipient_name": recipient_name,
            "purpose": purpose,
            "tone": tone
        }
    )