# Ask Harry

**Ask Harry** is a local-first **RAG + Agent framework** for exploring how LLMs reason over real codebases using hybrid retrieval and tool-based workflows.
It demonstrates how modern AI systems combine semantic search, structured tools, and iterative reasoning to produce grounded answers.

The project compares multiple interaction patterns.

| Mode           | Purpose                              |
| -------------- | ------------------------------------ |
| **ask**        | simple semantic search (classic RAG) |
| **chat**       | conversational RAG                   |
| **agent**      | tool-using AI agent                  |
| **agent-chat** | conversational agent with reasoning  |

---
**Why this project exists**

Most AI demos rely solely on embeddings. In real-world applications, embeddings alone are often insufficient.
LLMs struggle to reason reliably over large codebases when limited to a single retrieval strategy.

Ask-Harry investigates how combining multiple capabilities to produce **grounded and explainable answers.**:

* semantic retrieval for conceptual similarity
* keyword search for precise matching
* file inspection for complete context
* tool-based reasoning for iterative exploration

The goal is to better understand how modern AI systems can produce answers that are:
* more accurate
* more explainable
* less dependent on prompt tuning alone


# Architecture Overview

```
User Query
   ↓
CLI Interface
   ↓
Prompt Templates
   ↓
Service Layer
   ↓
Planner (future)
   ↓
Tool Registry
   ↓
Retrieval Layer
   ↓
LLM (Ollama)
```
---

# Core Concepts

## 1. RAG (Retrieval Augmented Generation)

Simple RAG pipeline:

```
question
 ↓
embedding
 ↓
vector search
 ↓
context injection
 ↓
LLM answer
```

Used in:

```
ask
chat
```

Good for:

* conceptual questions
* summarization
* understanding architecture

---

## 2. Agent with Tools

Agent pipeline:

```
question
 ↓
LLM decides which tool to use
 ↓
tool executes
 ↓
LLM observes results
 ↓
repeat until confident
 ↓
final answer
```

Tools allow the model to:

* explore repository structure
* search keywords
* read full files
* perform semantic lookup

Used in:

```
agent
agent-chat
```

---

# Available Tools

| Tool               | Purpose                       |
| ------------------ | ----------------------------- |
| vector_search_tool | semantic search across chunks |
| grep_repo_tool     | fast keyword search           |
| read_file_tool     | read full file contents       |
| list_files_tool    | inspect repo structure        |

Hybrid retrieval:

```
semantic search + keyword search + file inspection
```

produces better grounding than embeddings alone.

---
# Tech Stack

* Python
* Ollama (local LLM inference)
* ChromaDB (vector storage)
* Nomic embeddings
* CLI interface
* modular service architecture
___
# Installation

### 1. Clone repo

```bash
git clone <github repo>
cd ask-harry
```

### 2. Create virtual environment

```
uv venv
source .venv/bin/activate
```

or

```
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```
uv pip install -e .
```

---

# Configuration

Copy the sample config and update values as needed:

```bash
cp .env.example .env
```

Key settings:

```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:7b
EMBEDDING_MODEL=nomic-embed-text:latest
CHUNK_SIZE=400
CHUNK_OVERLAP=75
TOP_K=8
LOG_LEVEL=INFO
DEBUG=False
```

---

# Usage

---

## 1. Ingest repository

```
ask-harry ingest /path/to/project
```

Creates embeddings and stores them in ChromaDB.

---

## 2. Ask (simple RAG)

```
ask-harry ask "where is auth implemented"
```

Pipeline:

```
embedding → vector search → answer
```

---

## 3. Chat (conversational RAG)

```
ask-harry chat
```

Example:

```
Ask Harry> how is config loaded?
Ask Harry> where is vector store initialized?
```

Maintains conversational context.

---

## 4. Agent (tool-based reasoning)

```
ask-harry agent "where is the llm client defined"
```

Agent decides which tools to call.

Example tool sequence:

```
list_files_tool
grep_repo_tool
read_file_tool
```

---

## 5. Agent Chat

```
ask-harry agent-chat
```

Interactive tool-based reasoning.

Commands:

```
exit
clear
help
```

---
# Learning Focus

This project helps understand:

### embeddings

how semantic similarity impacts retrieval relevance

### chunking

how chunk size impacts retrieval quality

### hybrid retrieval

combining:

* semantic similarity
* keyword search
* file inspection

### tool-based reasoning

how LLMs:

* decide what to search
* refine context
* validate answers

---

# Design Philosophy

Transparent AI systems are easier to trust and improve.

This project keeps:

* components small
* logic explicit
* behavior observable

so each part of the pipeline can be understood independently.

---

# Future Improvements

planned experiments:

* reranking retrieved chunks
* deduplicating overlapping chunks
* planner layer for tool routing
* multi-step reasoning memory
* evaluation dataset
* benchmark prompts
* tool confidence scoring

---

# License

MIT

---
