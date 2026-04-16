import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest, ChatResponse
from app.memory import init_db, save_message, get_full_history, clear_session
from app.brain import process_message

app = FastAPI(
    title="Honeypot AI Chatbot",
    description="An AI-powered honeypot designed to detect and counter scammer attacks.",
    version="1.0.0"
)

# Constrain CORS for security purposes (Security Criteria)
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://honeypot-71374216638.us-central1.run.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Initialize Database
init_db()

# Serve Static Files (Frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", summary="Serve frontend UI")
async def read_root():
    """Returns the main chat dashboard interface."""
    return FileResponse('static/index.html')

@app.post("/api/chat", response_model=ChatResponse, summary="Process a chat message")
async def chat_endpoint(request: ChatRequest):
    """
    Takes a user message, processes it through the honeypot AI agent, 
    saves both user and AI messages to the DB, and returns the response.
    """
    try:
        # 1. Save User Message
        save_message(request.session_id, "user", request.message)
        
        # 2. Process with AI
        ai_result = await process_message(request.session_id, request.message)
        
        # 3. Save AI Response
        save_message(
            request.session_id, 
            "assistant", 
            ai_result.get("response", ""), 
            meta=ai_result
        )
        
        return ChatResponse(**ai_result)
    except Exception as e:
        import traceback
        with open("system_error.log", "a") as f:
            f.write(f"\n--- CRITICAL API ERROR ---\n{str(e)}\n{traceback.format_exc()}\n")
        print(f"CRITICAL ERROR: {e}")
        return {
            "intent": "UNKNOWN",
            "risk_level": "CRITICAL",
            "confidence_score": 0.0,
            "response": "System Error: Internal Server Error. Please check system_error.log.",
            "recommended_action": "IGNORE",
            "log_required": True,
            "extracted_info": {}
        }

# --- Honeypot API Endpoint ---
from app.models import HoneyPotRequest, HoneyPotResponse
from app.brain import generate_final_report

@app.post("/honeypot", response_model=HoneyPotResponse)
async def honeypot_endpoint(request: HoneyPotRequest):
    try:
        # 1. Save User Message (map HoneyPot format to internal)
        # Note: We rely on the internal logic to handle history, but we should ensure
        # the session is consistent.
        save_message(request.sessionId, "user", request.message.text)
        
        # 2. Process with AI
        ai_result = await process_message(request.sessionId, request.message.text)
        
        # 3. Save AI Response
        save_message(
            request.sessionId, 
            "assistant", 
            ai_result.get("response", ""), 
            meta=ai_result
        )
        
        # 4. Check if we should include final output
        # If the turn count is high (e.g. > 8) OR specific stop condition met
        # For now, we just return the standard reply.
        # Ideally, there should be a separate mechanism or the platform checks a separate log.
        # BUT, the docs say "End: You submit a final output...".
        # It doesn't explicitly say returned in the last API call, but "to the session log".
        # We will log it internally and maybe expose it via a separate endpoint if needed.
        
        # 5. Generate Final Report (Internal Logging)
        final_report = generate_final_report(request.sessionId)
        # We can also print/log this for debugging
        print(f"Final Report for {request.sessionId}: {final_report}")
        
        return HoneyPotResponse(
            reply=ai_result.get("response", "System Error"),
            riskLevel=ai_result.get("risk_level", "LOW")
        )
    except Exception as e:
        print(f"Honeypot Endpoint Error: {e}")
        return HoneyPotResponse(reply="System Error", riskLevel="CRITICAL")

@app.get("/api/results/{session_id}", summary="Get final report")
async def get_results(session_id: str):
    """Expose the final report for a session manually."""
    return generate_final_report(session_id)

@app.get("/api/history/{session_id}", summary="Retrieve conversation history")
async def get_history_endpoint(session_id: str):
    """Fetches the full conversation history for a given session."""
    return get_full_history(session_id)

@app.delete("/api/reset/{session_id}", summary="Reset a session")
async def reset_session(session_id: str):
    """Clears all memory and messages associated with a session ID."""
    clear_session(session_id)
    return {"status": "success", "message": "Session cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
