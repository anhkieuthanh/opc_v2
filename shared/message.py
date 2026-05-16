from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class MessageType(str, Enum):
    TASK = "task"
    REPORT = "report"
    ERROR = "error"


@dataclass
class Payload:
    content: str
    context: dict = field(default_factory=dict)
    priority: str = "normal"


@dataclass
class OPCMessage:
    from_agent: str
    to: str
    type: MessageType
    payload: Payload
    message_id: str = field(default_factory=lambda: str(uuid4()))
    thread_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "from": self.from_agent,
            "to": self.to,
            "thread_id": self.thread_id,
            "type": self.type.value,
            "payload": {
                "content": self.payload.content,
                "context": self.payload.context,
                "priority": self.payload.priority,
            },
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OPCMessage":
        return cls(
            message_id=data["message_id"],
            from_agent=data["from"],
            to=data["to"],
            thread_id=data["thread_id"],
            type=MessageType(data["type"]),
            payload=Payload(
                content=data["payload"]["content"],
                context=data["payload"].get("context", {}),
                priority=data["payload"].get("priority", "normal"),
            ),
            created_at=data["created_at"],
        )
