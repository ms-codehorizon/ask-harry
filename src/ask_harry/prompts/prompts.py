# Prompt templates


def normalize_question(question: str) -> str:
    return f"""
Rewrite this search query to fix typos and use standard technical terms. Only return the 
corrected string: {question}
    """


def build_direct_prompt(question: str):
    return f"""
You are Harry, a helpful AI assistant for repository questions.

The user is making a conversational request rather than asking about repository code.
Respond naturally and briefly. Do not mention retrieval, embeddings, or repository context
unless the user asks about the codebase directly.

User message:
{question}

Answer:
""".strip()


def build_routing_prompt(question: str):
    return f"""
You are a query router for a repository assistant.

Classify the user's message into exactly one of these labels:
- DIRECT: casual conversation, greetings, thanks, or general chat that should go straight to the LLM
- REPOSITORY: questions that need repository knowledge, code retrieval, or file context

Return only one word: DIRECT or REPOSITORY.

User message:
{question}

Label:
""".strip()


def build_prompt(context: str, question: str):
    return f"""
You are a senior software engineer analyzing a code repository.

Answer the question using ONLY the provided context.

Strict rules:
1. Only state facts that are explicitly present in the context.
2. Do NOT infer implementation details that are not clearly shown.
3. If the provided context is completely empty or unrelated to the question, 
   respond exactly with: "I couldn't find any relevant code in the repository to answer that." 
   However, if you can answer any part of the question using the context, 
   provide that information and do NOT include the failure message.
4. Do not assume common patterns or typical implementations.
5. Prefer quoting or closely paraphrasing the context rather than interpreting it.
6. Keep the answer concise and technical.

Citation rules:
- Every factual statement must include a citation using the provided numeric id.
- Do not use the word citation, use square brackets instead.
- Use citation format: [1]
- Do not invent citations.
- Do not cite IDs that are not present in the context.
- Do not include file names or paths in the answer text.
- Prefer information from implementation files over test files when both are available.

Context:
{context}

Question:
{question}

Answer:
"""
# 3. If the context does not explicitly answer the question, respond exactly with:
#   "I don't know based on the provided code."

def build_structured_prompt(context: str, question: str):
    return f"""
You are answering questions about a software repository.

Use ONLY the provided context.

Return output in JSON format:

{{
  "summary": short answer,
  "relevant_files": [],
  "confidence": 0-1
}}

Rules:
- only include files present in context
- do not invent file names
- keep summary concise
- confidence reflects certainty level

Context:
{context}

Question:
{question}
""".strip()
