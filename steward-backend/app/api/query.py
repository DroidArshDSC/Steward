from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def query_steward(payload: dict):
    question = payload.get("question", "No question provided.")
    
    # Mocked sample responses for testing
    mock_answers = {
        "how to setup project": "To set up the project, clone the repo and run `uvicorn main:app --reload`.",
        "who are you": "I’m Steward — your AI onboarding copilot.",
        "what is this project": "This is an AI onboarding assistant that answers engineering questions."
    }

    # Find a response if available
    answer = None
    for key, val in mock_answers.items():
        if key in question.lower():
            answer = val
            break

    # Default fallback
    if not answer:
        answer = "I'm running in mock mode right now. Once OpenAI access is back, I’ll give real, contextual answers."

    return {
        "question": question,
        "answer": answer,
        "mode": "mock"
    }
