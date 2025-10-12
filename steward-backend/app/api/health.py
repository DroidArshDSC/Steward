import os
from fastapi import APIRouter
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

@router.get("/")
async def health_check():
    """
    Checks whether the OpenAI API key is valid.
    Returns API status and model test response.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "❌ OPENAI_API_KEY not found in environment."}

    try:
        client = OpenAI(api_key=api_key)
        models = client.models.list()
        # Just fetch the first model name as a sanity check
        first_model = models.data[0].id if models.data else "unknown"
        return {
            "status": "ok",
            "message": "✅ OpenAI API key is valid.",
            "model_detected": first_model
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Invalid or unreachable API key. Details: {str(e)}"
        }
