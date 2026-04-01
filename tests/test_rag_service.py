from unittest.mock import patch

from ask_harry.services.rag_service import ask_question, chat_bot, route_question


def test_bypasses_retrieval_for_simple_greeting():
    with patch(
        "ask_harry.services.rag_service.generate",
        side_effect=["DIRECT", "Hello!"],
    ) as generate_mock, patch(
        "ask_harry.services.rag_service.embed"
    ) as embed_mock:
        answer, sources = ask_question("hi")

    assert answer == "Hello!"
    assert sources == {}
    assert generate_mock.call_count == 2
    embed_mock.assert_not_called()


def test_uses_retrieval_for_repository_question():
    fake_chunks = [{"text": "def foo(): pass", "source": "/tmp/app.py", "distance": 0.1}]

    with patch("ask_harry.services.rag_service.embed", return_value=[0.1, 0.2]), patch(
        "ask_harry.services.rag_service.search", return_value=fake_chunks
    ), patch("ask_harry.services.rag_service.generate", return_value="Repo answer") as generate_mock:
        answer, sources = ask_question("where is foo defined?")

    assert answer == "Repo answer"
    assert sources == {1: "/tmp/app.py"}
    assert generate_mock.call_count == 2


def test_chat_bot_bypasses_retrieval_for_simple_greeting():
    with patch("ask_harry.services.rag_service.is_populated", return_value=True), patch(
        "ask_harry.services.rag_service.generate",
        side_effect=["DIRECT", "Hey there"],
    ) as generate_mock, patch("ask_harry.services.rag_service.embed") as embed_mock:
        stream, sources = chat_bot("hello")

    assert "".join(stream) == "Hey there"
    assert sources == {}
    assert generate_mock.call_count == 2
    embed_mock.assert_not_called()


def test_route_question_returns_direct_for_chatty_input():
    with patch("ask_harry.services.rag_service.generate", return_value="DIRECT"):
        assert route_question("hi") == "DIRECT"


def test_route_question_returns_repository_for_code_question():
    with patch("ask_harry.services.rag_service.generate", return_value="REPOSITORY"):
        assert route_question("how does ingest work?") == "REPOSITORY"


def test_route_question_defaults_to_repository_on_unexpected_output():
    with patch("ask_harry.services.rag_service.generate", return_value="maybe"):
        assert route_question("how does ingest work?") == "REPOSITORY"
