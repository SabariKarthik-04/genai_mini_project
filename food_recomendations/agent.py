from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
import os
from .tools import find
from google.adk.sessions import InMemorySessionService
from .system_prompt import SYSTEM_PROMPT
from google.adk.runners import Runner
from google.genai import types 

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")






async def image_search(tool_context, base64_string):
    APP_NAME = "food_recomendations"
    USER_ID = "user_1"
    SESSION_ID = "session_001"
    session_service = InMemorySessionService()
    session = await session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(
        agent=vision_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    print("🚀 Running agent with image...")

    if tool_context is None:
        raise ValueError("tool_context is required")

    # ✅ Clean base64
    if base64_string.startswith("data:"):
        base64_string = base64_string.split(",")[1]

    base64_string = base64_string.strip().replace("\n", "").replace(" ", "")

    # ✅ Build content
    # vision_payload = [
    #     {"type": "text", "text": "List the raw food ingredients in this image. Comma-separated only."},
    #     {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_string}"}}
    # ]
    vision_payload = types.Content(
    role="user",
    parts=[
        types.Part(
            text=f"data:image/jpeg;base64,{base64_string}"
        )
        # types.Part(
        #     inline_data=types.Blob(
        #         mime_type="image/jpeg",
        #         data=
        #     )
        # )
    ]
)
    

    # ✅ Inject into context
    # tool_context.messages = [vision_payload]
    final_text = ""

    # ✅ RUN AGENT
    async for event in runner.run_async(user_id=USER_ID,session_id=SESSION_ID,new_message=vision_payload):
        if event.is_final_response():
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final_text += part.text

    return final_text.strip()

vision_model = LiteLlm(
    model="groq/meta-llama/llama-4-scout-17b-16e-instruct", 
    drop_params=True,
    temperature=0.1
)
vision_agent = Agent(
    model=vision_model,
    name="fridge_inspector",
    instruction="Analyze the image and return a comma-separated list of raw ingredients."
)

groq_model = LiteLlm(
    model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
    drop_params=True, 
    temperature=0.5
    )
root_agent = Agent(
    model=groq_model,
    name='groq_ai_agent',
    description='Assistant that identifies ingredients and finds recipes.',
    instruction=SYSTEM_PROMPT,
    tools=[find,image_search]
)


