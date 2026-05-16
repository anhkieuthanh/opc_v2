import asyncio
from agents.base.agent import BaseAgent


class MarketingAgent(BaseAgent):
    def __init__(self):
        super().__init__("agents/marketing/config.yaml")


if __name__ == "__main__":
    asyncio.run(MarketingAgent().start())
