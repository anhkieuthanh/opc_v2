import asyncio

from agents.base.agent import BaseAgent
from shared.message import MessageType, OPCMessage, Payload


class CEOAgent(BaseAgent):
    def __init__(self):
        super().__init__("agents/ceo/config.yaml")

    async def _on_response(self, original: OPCMessage, response_text: str) -> None:
        queues = self._route(response_text)
        if queues:
            await asyncio.gather(
                *[
                    self._queue.publish(
                        q,
                        OPCMessage(
                            from_agent=self._agent_id,
                            to=q,
                            thread_id=original.thread_id,
                            type=MessageType.TASK,
                            payload=Payload(
                                content=response_text,
                                priority=original.payload.priority,
                            ),
                        ),
                    )
                    for q in queues
                ]
            )

        await self._queue.publish(
            "gateway",
            OPCMessage(
                from_agent=self._agent_id,
                to="gateway",
                thread_id=original.thread_id,
                type=MessageType.REPORT,
                payload=Payload(content=response_text),
            ),
        )


if __name__ == "__main__":
    asyncio.run(CEOAgent().start())
