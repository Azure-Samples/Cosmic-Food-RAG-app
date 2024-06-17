from dataclasses import dataclass


@dataclass
class JSONDataPoint:
    name: str | None = None
    description: str | None = None
    price: str | None = None
    category: str | None = None
    collection: str | None = None


@dataclass
class Thought:
    title: str | None = None
    description: str | None = None


@dataclass
class DataPoint:
    json: list[JSONDataPoint]


@dataclass
class Context:
    data_points: DataPoint
    thoughts: list[Thought]


@dataclass
class Message:
    content: str | None = None
    role: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {"content": self.content, "role": self.role}


@dataclass
class RetrievalResponse:
    context: Context
    message: Message
    session_state: str
