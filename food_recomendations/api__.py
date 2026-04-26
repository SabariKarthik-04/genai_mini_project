import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import root_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_service = InMemorySessionService()

APP_NAME = "food_recommendations"

class SessionItem(BaseModel):
    userId: str
    sessionid: str

class InlineData(BaseModel):
    mime_type: str
    data: str  # base64

class PartModel(BaseModel):
    text: Optional[str] = None
    inline_data: Optional[InlineData] = None

class ChatRequest(BaseModel):
    userId: str
    sessionid: str
    parts: List[PartModel]


@app.post('/session')
async def create_session(item: SessionItem):
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=item.userId,
        session_id=item.sessionid
    )
    return {"message": "Session created", "session": session}


@app.post('/chat')
async def chat(req: ChatRequest):
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=APP_NAME
    )

    adk_parts = []

    for p in req.parts:
        if p.text:
            adk_parts.append(types.Part(text=p.text))

        elif p.inline_data:
            adk_parts.append(
                types.Part(
                    inline_data=types.Blob(
                        mime_type=p.inline_data.mime_type,
                        data=p.inline_data.data
                    )
                )
            )

    payload = types.Content(
        role="user",
        parts=adk_parts
    )

    final_text = ""

    async for event in runner.run_async(
        user_id=req.userId,
        session_id=req.sessionid,
        new_message=payload
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final_text += part.text
                        
    return {"response": final_text.strip()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)