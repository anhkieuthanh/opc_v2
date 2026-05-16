import asyncio
from agents.base.agent import BaseAgent


class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__("agents/sales/config.yaml")


if __name__ == "__main__":
    asyncio.run(SalesAgent().start())
