import os
from typing import List, Dict, Any

SYSTEM_PROMPT = """You are India's premier Drone Intelligence System AI assistant.
Your goal is to provide accurate, authoritative, and structured technical and regulatory answers regarding drones in India based strictly on retrieved knowledge context.

Rules:
1. Always base your answers on the provided Context & Citations.
2. Structure your response cleanly using GitHub-style markdown (headings, tables, bullet points).
3. Always include explicit source citations at the bottom or inline (e.g. `[Source: DGCA Handbook / rules_regulations.json]`).
4. If the context does not contain enough information, state what is known from the context and clearly outline any caveats.
"""

class RAGGenerator:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    def generate_response(self, query: str, context: str, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        # 1. Try OpenAI if API key available
        if self.openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.openai_key)
                prompt = f"Retrieved Context:\n{context}\n\nUser Question: {query}\n\nPlease answer the user question based on the context above."
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )
                answer_text = response.choices[0].message.content
                return self._package_result(answer_text, docs)
            except Exception as e:
                print(f"[Generator] OpenAI generation error: {e}")

        # 2. Fallback to Smart Domain-Aware Synthesis Engine
        answer_text = self._synthesize_local_answer(query, docs)
        return self._package_result(answer_text, docs)

    def _package_result(self, answer_text: str, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        citations = []
        for d in docs:
            citations.append({
                "id": d["id"],
                "source": d["metadata"].get("source", "Unknown"),
                "title": d["metadata"].get("title", "Reference"),
                "score": d.get("score", 0.0),
                "snippet": d["content"][:180] + "..."
            })
        return {
            "answer": answer_text,
            "citations": citations
        }

    def _synthesize_local_answer(self, query: str, docs: List[Dict[str, Any]]) -> str:
        if not docs:
            return "I searched the India Drone Intelligence Knowledge Base, but could not find specific matches for your query. Please rephrase or try another search term."

        lines = [
            f"### Drone Intelligence Response: {query.strip('?').title()}\n",
            "Based on the **DGCA Drone Rules & Indian Drone Ecosystem Knowledge Base**, here are the details:\n"
        ]

        for i, d in enumerate(docs, 1):
            title = d["metadata"].get("title", f"Document {i}")
            source = d["metadata"].get("source", "Knowledge Base")
            content = d["content"].strip()
            lines.append(f"#### {i}. {title}")
            lines.append(f"{content}\n")
            lines.append(f"*Source: [{source}]*\n")

        lines.append("\n---\n**Summary & Compliance Notes:**")
        lines.append("- Ensure all flights adhere to **Drone Rules 2021** (amended 2023).")
        lines.append("- Check airspace zone on the **DigitalSky Portal** before taking off.")
        lines.append("- Operating micro or small drones for commercial purposes requires a **Remote Pilot Certificate (RPC)** from a DGCA-approved RPTO.")

        return "\n".join(lines)
