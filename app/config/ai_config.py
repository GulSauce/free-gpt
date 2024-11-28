import os
from dotenv import load_dotenv
import chainlit as cl
from openai import AsyncOpenAI
client = AsyncOpenAI()

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Instrument the OpenAI client
cl.instrument_openai()

settings = {
    "model": "o1-mini",
}