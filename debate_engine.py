# debate_engine.py
from dataclasses import dataclass
from typing import List, Dict, Tuple
from config import AppConfig
import time
from api_client import AIClient
import random

@dataclass
class Message:
    role: str
    content: str
    model: str
    timestamp: float = None
    stance: str = None  # Added stance field to track position

    def __post_init__(self):
        self.timestamp = self.timestamp or time.time()

class DebateEngine:
    def __init__(self, config: AppConfig, client: AIClient):
        self.config = config
        self.client = client
        self.conversation: List[Message] = []
        self._initialize_conversation()
        self.stance_summary: Dict[str, List[str]] = {"left": [], "right": []}
        self.current_agent_index = 0  # Track which agent's turn it is

    def _initialize_conversation(self):
        for agent in self.config.agents.values():
            debate_prompt = f"""You are a strong {agent.stance} advocate in this debate.
            CRITICAL RULES:
            1. ALWAYS take the most extreme {agent.stance} position possible
            2. NEVER compromise or agree with the opponent
            3. Use provocative and strong language
            4. Attack opponent's viewpoint aggressively
            5. Make bold, definitive statements
            6. Never take middle ground positions
            
            Your core beliefs: {agent.core_beliefs}"""
            
            self.conversation.append(Message(
                role="system",
                content=debate_prompt,
                model=agent.model,
                stance=agent.stance
            ))

    def add_user_message(self, content: str):
        self.current_topic = content
        self.current_agent_index = 0  # Reset agent index when new topic starts

    def _summarize_stance(self, message: Message):
        if message.stance in ["left", "right"]:
            sentences = message.content.split('.')
            key_points = [s.strip() for s in sentences if len(s.split()) > 5][:3]
            self.stance_summary[message.stance].extend(key_points)

    def generate_responses(self, num_turns: int = 1) -> List[str]:
        """Generate a response from one agent at a time, alternating between them."""
        all_responses = []

        # Add the user message if it's not already in the conversation
        if not any(msg.role == "user" for msg in self.conversation):
            self.conversation.append(Message(role="user", content=self.current_topic, model="", stance=""))

        # Get list of agents for easy indexing
        agents = list(self.config.agents.items())
        
        # Get the current agent's turn
        agent_name, agent_config = agents[self.current_agent_index]

        try:
            # Build the conversation history
            messages = [
                {"role": msg.role, "content": msg.content, "model": msg.model}
                for msg in self.conversation
            ]

            # Generate response for current agent
            response = self.client.generate_response(messages, agent_config.model)
            message = Message(
                role="assistant",
                content=response,
                model=agent_config.model,
                stance=agent_config.stance
            )
            self.conversation.append(message)
            self._summarize_stance(message)
            all_responses.append(response)

            # Update the index for next turn, cycling back to 0 if needed
            self.current_agent_index = (self.current_agent_index + 1) % len(agents)

        except Exception as e:
            error_message = f"Error generating response from {agent_config.name}: {str(e)}"
            print(error_message)
            all_responses.append(error_message)

        return all_responses