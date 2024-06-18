from dataclasses import dataclass


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
    role: str | None = None

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
    session_state: str

    def to_dict(self) -> dict[str, dict[str, list[dict[str, str | None]]] | dict[str, str | None] | str]:
        """
        Converts the object to a dictionary representation.

        Returns:
            A dictionary representation of the object.
        """
        return {
            "context": self.context.to_dict(),
            "message": self.message.to_dict(),
            "session_state": self.session_state,
        }
