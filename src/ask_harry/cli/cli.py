# Entry point for commands.

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from ask_harry.config.settings import Config
from ask_harry.services.ingest_service import ingest_repo
from ask_harry.services.rag_service import ask_question, chat_bot, agent_question, clear_chat_history
from ask_harry.utils.utils import clean_text, format_grouped_citations, logger

app = typer.Typer()
console = Console(force_interactive=True)
config = Config()
#config.debug_print()


@app.command()
def ingest(path: Annotated[Path, typer.Argument(help="Path to the repository/directory.")]):
    """Ingest a repository into the vector database
    usage: ask-harry ingest path/to/repo"""
    repo_path = path.expanduser()
    logger.info(f"Ingesting: {repo_path}...")
    ingest_repo(repo_path)
    logger.info("Done.")


@app.command()
def ask(question: str, json: bool = False):
    """Ask a question about the ingested data
    usage: ask-harry ask question [optional: --json]"""
    print(f"Question: {question}")
    answer, sources = ask_question(question,json)
    answer, citations = format_grouped_citations(answer, sources)
    print("Answer:")
    print(answer)
    if len(citations) > 0:
        print("\nSources:")
        for file, ids in citations:
            print(f"{file} -> {ids}")


@app.command()
def chat():
    """Chat with the bot. Ask questions related to the ingested repository.
    usage: ask-harry chat"""
    try:
        while True:
            query = console.input("\n[bold cyan]Ask Harry>[/] ")
            if len(query) <= 0:
                continue
            if query.lower() in ["exit", "quit"]:
                break
            if query.lower() in ["help"]:
                console.print(
                    "\n[bold brown]Type to ask Harry a question. Type 'exit' or 'quit' to exit."
                )
                continue

            better_query = clean_text(query)
            logger.info(f"Original: {query} -> Fixed: {better_query}")
            # Call the chat function
            # shows a spinner and "Thinking" text
            with console.status("[bold brown]Harry is analyzing the code..."):
                stream, source_map = chat_bot(better_query)

            full_answer = ""
            # Once the 'with' block ends, the spinner vanishes
            console.print("[bold green]Harry:[/][white] ", end="")
            for text_chunk in stream:
                console.print(text_chunk, end="")
                full_answer += text_chunk

            # we cannot pass the stream directly to formatted_citations, let stream finish first
            answer, citations = format_grouped_citations(full_answer, source_map)

            if len(citations) > 0:
                console.print("\n[bold green]Sources:")
                for file, ids in citations:
                    console.print(f"{file} -> {ids}")
    except Exception as e:
        console.print(f"[bold red]Error: {e}")


@app.command()
def agent(question: str):
    """Ask one shot question regarding loaded repository using tool-calling agent.
    usage: ask-harry agent question"""
    agent_question(question)

@app.command("agent-chat")
def agent_chat():
    """Ask tool-calling agent questions using chat style related to loaded repository.
    usage: ask-harry agent-chat"""
    try:
        while True:
            query = console.input("\n[bold cyan]Ask Harry>[/] ")
            if len(query) <= 0:
                continue
            if query.lower() in ["exit", "quit"]:
                break
            if query.lower() in ["clear"]:
                clear_chat_history()
                continue
            if query.lower() in ["help"]:
                console.print(
                    "\n[bold brown]Type to ask Harry a question. Type 'exit' or 'quit' to exit."
                )
                continue
            agent_question(query)

    except Exception as e:
        console.print(f"[bold red]Error: {e}")

if __name__ == "__main__":
    app()
