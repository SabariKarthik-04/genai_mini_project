import ast
from utils.data_injestion_pipeline import Data_Ingestion_Pipeline

def main():
    data_ingestion_pipeline = Data_Ingestion_Pipeline()
    data_ingestion_pipeline.data_ingestion_handler()
    

def find(query: str, top_k: int):
    pipeline = Data_Ingestion_Pipeline() 
    results = pipeline.similarity_search_handler(query=query, top_k=top_k)

    if not (isinstance(results, dict) and "metadatas" in results and results["metadatas"]):
        return "No recipes found. Please ask the user for different ingredients."

    raw_list = results["metadatas"][0]
    formatted_output = ""
    
    user_items = [item.strip().lower() for item in query.split(",")]

    for recipe in raw_list:
        name = recipe.get("name", "Unknown Dish").title()
        minutes = recipe.get("minutes", "Unknown")
        
        ing_raw = recipe.get("ingredients", "[]")
        try:
            recipe_ings = ast.literal_eval(ing_raw) if isinstance(ing_raw, str) else ing_raw
        except:
            recipe_ings = [str(ing_raw)]
        
        ing_str = ", ".join(recipe_ings) if isinstance(recipe_ings, list) else str(recipe_ings)


        you_have = []
        missing = []
        for r_ing in recipe_ings:
            if any(u in r_ing.lower() for u in user_items):
                you_have.append(r_ing)
            else:
                missing.append(r_ing)
                
        you_have_str = ", ".join(you_have) if you_have else "None"
        missing_str = ", ".join([f"{m} **(ESSENTIAL)**" for m in missing]) if missing else "None"


        steps_raw = recipe.get("steps", "[]")
        try:
            steps_list = ast.literal_eval(steps_raw) if isinstance(steps_raw, str) else steps_raw
        except:
            steps_list = [str(steps_raw)]
            
        steps_str = "\n".join([f"   {i+1}. {step.capitalize()}" for i, step in enumerate(steps_list)])

        tags_raw = recipe.get("tags", "[]")
        try:
            tags_list = ast.literal_eval(tags_raw) if isinstance(tags_raw, str) else tags_raw
        except:
            tags_list = []

        tags_str = " ".join([f"#{str(tag).replace(' ', '').replace('-', '')}" for tag in tags_list[:3]])

        formatted_output += f"**-- Name:** {name}  \n"
        formatted_output += f"**-- Ingredients:** {ing_str}  \n"
        formatted_output += f"**-- Ingredient Match:** \n"
        formatted_output += f"  * **You Have:** {you_have_str}  \n"
        formatted_output += f"  * **Missing:** {missing_str}  \n"
        formatted_output += f"**-- Minutes to Make:** {minutes}  \n"
        formatted_output += f"**-- Steps:** \n{steps_str}  \n"
        formatted_output += f"**-- Tags:** {tags_str}  \n\n"
        formatted_output += "---\n\n"

    return formatted_output

