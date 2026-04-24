from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
import os
from tools import find
from system_prompt import SYSTEM_PROMPT

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")



async def image_search(base64_string: str, tool_context=None) -> str:
    print("👁️ Vision Tool analyzing image...")
    
    # Wrap the logic in a standard payload list
    vision_payload = [
        {"type": "text", "text": "List the raw food ingredients in this image. Comma-separated only."},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_string}"}}
    ]
    
    detected_ingredients = ""
    
    async for chunk in vision_agent.run_async(
        vision_payload, 
        parent_context=tool_context
    ):
        if hasattr(chunk, 'text'):
            detected_ingredients += chunk.text
        else:
            detected_ingredients += str(chunk)
            
    return detected_ingredients.strip()

vision_model = LiteLlm(
    model="groq/llama-3.2-11b-vision-preview", 
    drop_params=True,
    temperature=0.1
)
vision_agent = Agent(
    model=vision_model,
    name="fridge_inspector",
    instruction="Analyze the image and return a comma-separated list of raw ingredients."
)

groq_model = LiteLlm(
    model="groq/openai/gpt-oss-20b",
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


