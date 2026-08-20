from src.agents.llm import get_chat_model
from src.graph.db import Neo4jConnection
from src.retrieval.hybrid import HybridRetriever


class NotesAgent:
    """Generates concise, structured short notes (as markdown) for a concept."""

    def __init__(self, conn: Neo4jConnection):
        self.conn = conn
        self.llm = get_chat_model(temperature=0.3)

    def generate_notes(self, concept_name: str, student_id: str) -> str:
        # Fetch concept description from Neo4j
        concept_res = self.conn.query(
            "MATCH (c:Concept) WHERE toLower(c.name) CONTAINS toLower($name) "
            "RETURN c.name AS name, c.description AS desc LIMIT 1",
            {"name": concept_name},
        )
        concept_desc = ""
        canonical_name = concept_name
        if concept_res and concept_res[0].get("desc"):
            concept_desc = concept_res[0]["desc"]
            canonical_name = concept_res[0].get("name", concept_name)

        # Retrieve related context from student's uploaded materials
        retriever = HybridRetriever(self.conn)
        results = retriever.retrieve(concept_name, student_id, top_k=5)
        chunks = [r.get("content", r.get("concept", "")) for r in (results or [])]
        context_str = "\n\n".join(chunks) if chunks else "No additional context found."

        prompt = f"""You are an expert academic note-taker. Generate concise, well-structured short notes for the topic: "{canonical_name}".

Use the following context from the student's study materials:
<context>
{f'Concept Description: {concept_desc}' if concept_desc else ''}

{context_str}
</context>

Format your response as clean Markdown with these sections:
## 📌 Key Idea
One or two sentences summarizing the core concept.

## 🧠 Main Points
- Bullet points covering the 4–6 most important facts, definitions, or ideas.

## 🔗 How It Connects
Brief note on how this concept relates to other ideas or prerequisites.

## ⚡ Quick Formula / Rule (if applicable)
Any key formula, rule, or mnemonic worth remembering. Skip this section if not applicable.

## 💡 Example
One concrete, simple example to illustrate the concept.

Keep the total length under 300 words. Use plain language a student can quickly scan during revision.
"""

        response = self.llm.invoke(prompt)
        return response.content
