from dataclasses import dataclass
from enum import Enum


class AIChatRoles(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class RetrievalMode(str, Enum):
    HYBRID = "rag"
    VECTOR = "vector"
    KEYWORD = "keyword"


@dataclass
class DataPoint:
    """
    Class to represent a data point.
    """

    name: str | None = None
    description: str | None = None
    price: str | None = None
    category: str | None = None
    collection: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """
        Converts the object to a dictionary representation.

        Returns:
            A dictionary representation of the object.
        """
        return {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "collection": self.collection,
        }


@dataclass
class Thought:
    """
    Class to represent a thought.
    """

    title: str | None = None
    description: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """
        Converts the object to a dictionary representation.

        Returns:
            A dictionary representation of the object.
        """
        return {"title": self.title, "description": self.description}


@dataclass
class Context:
    """
    Class to represent a context consisting of data points and thoughts.
    """

    data_points: list[DataPoint]
    thoughts: list[Thought]

    def to_dict(self) -> dict[str, list[dict[str, str | None]]]:
        """
        Converts the object to a dictionary representation.

        Returns:
            A dictionary representation of the object.
        """
        return {
            "data_points": [data_point.to_dict() for data_point in self.data_points],
            "thoughts": [thought.to_dict() for thought in self.thoughts],
        }


@dataclass
class Message:
    """
    Class to represent a message.
    """

    content: str | None = None
    role: AIChatRoles = AIChatRoles.ASSISTANT

    def to_dict(self) -> dict[str, str | None]:
        """
        Converts the object to a dictionary representation.

        Returns:
            A dictionary representation of the object.
        """
        return {"content": self.content, "role": self.role}


@dataclass
class RetrievalResponse:
    """
    Class to represent a retrieval response.
    """

    context: Context
    message: Message
    sessionState: str

    def to_dict(self) -> dict[str, dict[str, list[dict[str, str | None]]] | dict[str, str | None] | str]:
        """
        Converts the object to a dictionary representation.

        Returns:
            A dictionary representation of the object.
        """
        return {
            "context": self.context.to_dict(),
            "message": self.message.to_dict(),
            "sessionState": self.sessionState,
        }


@dataclass
class RetrievalResponseDelta:
    """
    Class to represent a retrieval response for streaming.
    """

    context: Context | None = None
    delta: Message | None = None
    sessionState: str | None = None

    def to_dict(self) -> dict[str, dict[str, list[dict[str, str | None]]] | dict[str, str | None] | str | None]:
        """
        Converts the object to a dictionary representation.

        Returns:
            A dictionary representation of the object.
        """
        return {
            "context": self.context.to_dict() if self.context else None,
            "delta": self.delta.to_dict() if self.delta else None,
            "sessionState": self.sessionState if self.sessionState else None,
        }
