import os
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, google

from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, send_email

load_dotenv()  # load .env in current working directory

class ShinyAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                # Uses Gemini via livekit-plugins-google
                voice="Aoede",
                temperature=0.7,
            ),
            tools=[
                get_weather,
                send_email,
            ],
        )

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession()

    await session.start(
        room=ctx.room,
        agent=ShinyAgent(),
        room_input_options=RoomInputOptions(
            # Audio-only is fine; video can be enabled from Playground UI
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    # Start with a friendly introduction
    await session.generate_reply(instructions=SESSION_INSTRUCTION)

async def main():
    worker = agents.Worker(
        os.getenv("LIVEKIT_URL"),  # Pass as first positional argument
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
        agent_factory=ShinyAgent,
    )
    await worker.run()

if __name__ == "__main__":
    # Run as a worker that the Agents Playground can dispatch jobs to.
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
