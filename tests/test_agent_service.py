from unittest.mock import patch

from ask_harry.services.rag_service import agent_question, clear_chat_history


def setup_function():
    clear_chat_history()


def test_agent_question_bypasses_tools_for_direct_input():
    with patch("ask_harry.services.rag_service.route_question", return_value="DIRECT"), patch(
        "ask_harry.services.rag_service.generate", return_value="Hi there"
    ) as generate_mock, patch(
        "ask_harry.services.rag_service.display_agent_response"
    ) as display_mock:
        answer = agent_question("hi")

    assert answer == "Hi there"
    generate_mock.assert_called_once()
    display_mock.assert_called_once_with("Hi there")


def test_agent_question_requests_final_answer_after_empty_response():
    with patch("ask_harry.services.rag_service.route_question", return_value="REPOSITORY"), patch(
        "ask_harry.services.rag_service.is_populated", return_value=True
    ), patch("ask_harry.services.rag_service.register_builtin_tools"), patch(
        "ask_harry.services.rag_service.load_prompt", return_value="system"
    ), patch.dict(
        "ask_harry.services.rag_service.TOOLS", {}, clear=True
    ), patch(
        "ask_harry.services.rag_service.chat_with_tools",
        side_effect=[{"content": ""}, {"content": "Final answer"}],
    ) as chat_mock, patch(
        "ask_harry.services.rag_service.display_agent_response"
    ) as display_mock:
        answer = agent_question("what does endpoint.py do?")

    assert answer == "Final answer"
    assert chat_mock.call_count == 2
    display_mock.assert_called_once_with("Final answer")
