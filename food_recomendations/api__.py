import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import root_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# 1. A simple Python list to act as our bulletproof memory container
chat_history = []

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    global chat_history
    
    # 2. Append the user message using the standard format LiteLLM expects
    chat_history.append({"role": "user", "content": req.message})
    
    full_response = ""
    
    # 3. Pass the entire history array directly to the agent.
    # This completely bypasses the Runner and forces the agent to read the whole context!
    async for chunk in root_agent.run_async(chat_history):
        # Extract the text exactly like you successfully did in your vision tool
        if hasattr(chunk, 'text'):
            full_response += chunk.text
        else:
            full_response += str(chunk)
            
    # 4. Save the agent's finalized reply back into the memory
    chat_history.append({"role": "assistant", "content": full_response.strip()})
    
    return {"reply": full_response.strip()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)