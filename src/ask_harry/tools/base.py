from dataclasses import dataclass
from typing import Any, Callable, Dict

@dataclass
class Tool:
    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any]

    def to_ollama_format(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }