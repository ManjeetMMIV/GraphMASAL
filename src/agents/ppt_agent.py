import json
from src.agents.llm import get_chat_model
from src.graph.db import Neo4jConnection
from src.retrieval.hybrid import HybridRetriever

class PPTAgent:
    def __init__(self, conn: Neo4jConnection):
        self.conn = conn
        self.llm = get_chat_model(temperature=0.7)

    def generate_slides_json(self, concept_name: str, student_id: str, custom_prompt: str = "") -> list:
        """
        Generates structured slide content (JSON) for a specific concept.
        Returns a list of dictionaries: [{"title": "...", "bullets": ["...", "..."]}, ...]
        """
        # Retrieve relevant concepts context
        retriever = HybridRetriever(self.conn)
        results = retriever.retrieve(concept_name, student_id, top_k=3)
        
        context_str = "No specific context found."
        if results:
            lines = []
            for r in results:
                lines.append(f"Related Concept: {r['concept']}")
            context_str = "\n".join(lines)
            
        # Fetch the exact concept description if it exists
        concept_query = "MATCH (c:Concept) WHERE toLower(c.name) CONTAINS toLower($name) RETURN c.description AS desc LIMIT 1"
        concept_res = self.conn.query(concept_query, {"name": concept_name})
        if concept_res and concept_res[0]["desc"]:
            context_str = f"Main Concept Description: {concept_res[0]['desc']}\n\n" + context_str

        # Handle custom instruction
        custom_instruction = ""
        if custom_prompt and custom_prompt.strip():
            custom_instruction = f"STUDENT'S CUSTOM INSTRUCTION: {custom_prompt.strip()}\nEnsure the presentation strictly follows this custom instruction."

        prompt = f"""
You are an expert educational instructional designer.
Your task is to create content for a PowerPoint presentation about the topic: "{concept_name}".

Use the following context from the student's learning materials to ground your explanation:
<context>
{context_str}
</context>

{custom_instruction}

Guidelines for the slides:
1. Create a Title slide (first slide) with the topic name as the title, and a brief subtitle as a bullet.
2. Create 3 to 5 content slides explaining the core concepts.
3. Each content slide must have a clear, concise "title".
4. Each content slide must have 2 to 4 short "bullets" (bullet points). Keep bullet points under 15 words each.
5. You MUST return ONLY a raw, valid JSON array. Do not include markdown codeblocks (no ```json). Do not include any conversational text.

Expected JSON format:
[
  {{
    "title": "Title of the Slide",
    "bullets": [
      "First bullet point here",
      "Second bullet point here"
    ]
  }}
]
"""
        
        response = self.llm.invoke(prompt)
        content = response.content.strip()
        
        # Clean up markdown if the LLM still returns it
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        try:
            slides = json.loads(content.strip())
            if not isinstance(slides, list):
                raise ValueError("JSON is not a list")
            return slides
        except json.JSONDecodeError as e:
            print(f"Error parsing PPT JSON: {e}")
            print(f"Raw output: {content}")
            # Fallback slide
            return [{
                "title": concept_name,
                "bullets": ["Could not generate specific slides due to an error.", "Please try again."]
            }]
