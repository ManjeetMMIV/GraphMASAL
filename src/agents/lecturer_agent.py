from src.agents.llm import get_chat_model
from src.graph.db import Neo4jConnection
from src.retrieval.hybrid import HybridRetriever

class LecturerAgent:
    def __init__(self, conn: Neo4jConnection):
        self.conn = conn
        self.llm = get_chat_model(temperature=0.7)

    def generate_script(self, concept_name: str, student_id: str) -> str:
        """
        Generates an engaging audio lecture script for a specific concept.
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
            
        # We can also fetch the exact concept description if it exists
        concept_query = "MATCH (c:Concept) WHERE toLower(c.name) CONTAINS toLower($name) RETURN c.description AS desc LIMIT 1"
        concept_res = self.conn.query(concept_query, {"name": concept_name})
        if concept_res and concept_res[0]["desc"]:
            context_str = f"Main Concept Description: {concept_res[0]['desc']}\n\n" + context_str

        prompt = f"""
You are an expert AI tutor and podcast host.
Your task is to write an engaging, conversational, and educational audio lecture script explaining the topic: "{concept_name}".

Use the following context from the student's learning materials to ground your explanation:
<context>
{context_str}
</context>

Guidelines for the script:
1. Speak directly to the listener in a warm, encouraging tone.
2. Explain the core idea simply, using an analogy if helpful.
3. Make it sound natural when spoken (avoid complex markdown or bullet points).
4. Do NOT include sound effects tags like [Sigh], [Music], or speaker labels like "Host:". Just pure spoken text.
5. Keep it concise, around 150-300 words.
"""
        
        response = self.llm.invoke(prompt)
        return response.content
