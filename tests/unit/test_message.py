from shared.message import MessageType, OPCMessage, Payload


def test_message_round_trip():
    msg = OPCMessage(
        from_agent="ceo",
        to="marketing",
        type=MessageType.TASK,
        payload=Payload(content="Run a campaign", priority="high"),
    )
    data = msg.to_dict()
    restored = OPCMessage.from_dict(data)

    assert restored.from_agent == "ceo"
    assert restored.to == "marketing"
    assert restored.type == MessageType.TASK
    assert restored.payload.content == "Run a campaign"
    assert restored.payload.priority == "high"
    assert restored.message_id == msg.message_id
    assert restored.thread_id == msg.thread_id


def test_message_default_priority():
    msg = OPCMessage(
        from_agent="sales",
        to="ceo",
        type=MessageType.REPORT,
        payload=Payload(content="Done"),
    )
    assert msg.payload.priority == "normal"


def test_message_type_values():
    assert MessageType.TASK == "task"
    assert MessageType.REPORT == "report"
    assert MessageType.ERROR == "error"
