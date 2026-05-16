import asyncio
from agents.base.agent import BaseAgent


class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__("agents/support/config.yaml")


if __name__ == "__main__":
    asyncio.run(SupportAgent().start())
