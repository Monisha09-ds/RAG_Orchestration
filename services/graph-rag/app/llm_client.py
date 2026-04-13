import json
import logging
from groq import Groq
from .config import Config

logger = logging.getLogger("graph_rag.llm")
groq_client = Groq(api_key=Config.GROQ_API_KEY)

def extract_graph_entities(text):
    logger.info(f"Extracting entities from text ({len(text)} chars)...")
    
    system_prompt = """
    You are an expert Knowledge Graph Engineer. Your task is to extract structured entities from portfolio text.
    
    CORE ENTITIES:
    - **Person**: The owner (name, role).
    - **Projects**: name, description, tech stack.
    - **Experience**: Job titles, Companies, Durations.
    - **Education**: Degrees, Universities, Years.
    - **Certifications**: Professional certs and awards.
    - **Skills/Tools**: Technologies and soft skills.
    
    NORMALIZATION RULES:
    1. Use canonical names (e.g., "Python", not "Python3" or "Python Programming").
    2. Capitalize Proper Nouns.
    3. If multiple versions of a tool exist, use the most common base name unless the version is critical.
    """

    user_prompt = f"""
    Analyze the following text:
    
    ---
    {text[:20000]} 
    ---
    
    Return a STRICT JSON object answering the schema below.
    
    JSON SCHEMA:
    {{
      "person": {{ "name": "Name", "role": "Role" }},
      "projects": [ {{ "name": "Name", "description": "...", "tech": ["Skill1"] }} ],
      "experience": [ {{ "company": "Name", "role": "Title", "period": "..." }} ],
      "education": [ {{ "institution": "Name", "degree": "...", "year": "..." }} ],
      "awards": [ "Award/Cert Name" ],
      "skills": [ "Skill1", "..." ],
      "tools": [ "Tool1", "..." ]
    }}
    """
    
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        logger.info("Entity extraction successful.")
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        logger.error(f"LLM Extraction failed: {e}")
        return None

def classify_intent(question):
    """
    Classifies the user question into one of the graph intents.
    """
    logger.info(f"Classifying intent for: '{question}'")
    
    system_prompt = """
    You are an intent classifier for a portfolio chatbot. 
    Classify the user question into exactly ONE of the following categories:
    
    - PERSON: Questions about name, role, contact, bio, or general info.
    - PROJECTS: Questions about projects, apps built, or technical contributions.
    - SKILLS: Questions about technologies, tools, skills, languages.
    - EDUCATION: Questions about university, degrees, certifications, or awards.
    - ALL: If it covers multiple topics, work experience/career, or is unclear.
    
    Return ONLY the category name (e.g., "PERSON").
    """
    
    try:
        completion = groq_client.chat.completions.create(
            # ... (no change to model/messages)
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0,
            max_tokens=10
        )
        intent = completion.choices[0].message.content.strip().upper()
        
        # Fallback if LLM gives something weird
        valid_intents = ["PERSON", "PROJECTS", "SKILLS", "TOOLS", "EDUCATION", "ALL"]
        if intent not in valid_intents:
            intent = "ALL"
            
        logger.info(f"Classified Intent: {intent}")
        return intent
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        return "ALL"

def generate_answer(question, facts, history=None):
    logger.info(f"Generating answer for: '{question}' with history length {len(history) if history else 0}")
    
    system_prompt = """
    You are a strict yet conversational Portfolio Assistant.
    
    CORE RULES:
    1. Answer ONLY using the provided FACTS.
    2. If the answer is NOT in the FACTS, and cannot be inferred from HISTORY, say: "I don't have that information available in the current knowledge base."
    3. Use HISTORY to resolve pronouns (e.g., "what about him?" refers to the person in previous turns).
    4. Keep answers concise (max 3 sentences).
    5. No marketing fluff.
    6. If the user greets you (e.g., "hi", "hello"), greet them back politely using the Person's name if available in FACTS.
    """

    history_text = ""
    if history:
        history_text = "CONVERSATION HISTORY:\n" + "\n".join([f"User: {h['role']}: {h['content']}" for h in history[-4:]])

    user_prompt = f"""
    {history_text}
    
    FACTS:
    {json.dumps(facts, indent=2)}

    CURRENT QUESTION:
    {question}
    """

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        answer = completion.choices[0].message.content.strip()
        logger.info("Answer generated.")
        return answer
    except Exception as e:
        logger.error(f"LLM Answer generation failed: {e}")
        return "I don't have that information available in the current knowledge base."
