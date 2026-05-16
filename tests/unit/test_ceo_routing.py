import pytest
from unittest.mock import AsyncMock, patch, MagicMock


def make_ceo():
    from agents.ceo.agent import CEOAgent
    with patch.dict("os.environ", {"RABBITMQ_URL": "amqp://test"}), \
         patch("agents.base.agent.RabbitMQClient"), \
         patch("agents.base.agent.build_provider"):
        return CEOAgent()


def test_route_marketing(tmp_path):
    agent = make_ceo()
    queues = agent._route("Chúng ta cần một chiến dịch marketing mới")
    assert "marketing" in queues


def test_route_sales(tmp_path):
    agent = make_ceo()
    queues = agent._route("Hãy cải thiện pipeline sale")
    assert "sales" in queues


def test_route_support(tmp_path):
    agent = make_ceo()
    queues = agent._route("Khách hàng phàn nàn về đơn hàng")
    assert "support" in queues


def test_route_no_match(tmp_path):
    agent = make_ceo()
    queues = agent._route("Hôm nay thời tiết đẹp")
    assert queues == []


def test_route_multiple(tmp_path):
    agent = make_ceo()
    queues = agent._route("marketing và sale cùng phối hợp")
    assert "marketing" in queues
    assert "sales" in queues
