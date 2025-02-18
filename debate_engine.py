from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import random
import time
import numpy as np
from collections import defaultdict
from config import AppConfig, AgentConfig 

# Base classes from original implementation
class DebateStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    CONCLUDED = "concluded"
    ERROR = "error"

class StanceType(Enum):
    LEFT = "left"
    RIGHT = "right"
    NEUTRAL = "neutral"

@dataclass
class Message:
    role: str
    content: str
    model: str
    timestamp: float = field(default_factory=time.time)
    stance: Optional[StanceType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "model": self.model,
            "timestamp": self.timestamp,
            "stance": self.stance.value if self.stance else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        if 'stance' in data and data['stance']:
            data['stance'] = StanceType(data['stance'])
        return cls(**data)

class DebateMetrics:
    def __init__(self):
        self.response_times: List[float] = []
        self.message_lengths: List[int] = []
        self.stance_strengths: Dict[StanceType, List[float]] = {
            StanceType.LEFT: [],
            StanceType.RIGHT: []
        }
        self.interaction_count: int = 0
        
    def update(self, message: Message, response_time: float):
        self.response_times.append(response_time)
        self.message_lengths.append(len(message.content))
        self.interaction_count += 1

    def get_average_response_time(self) -> float:
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "avg_response_time": self.get_average_response_time(),
            "avg_message_length": sum(self.message_lengths) / len(self.message_lengths) if self.message_lengths else 0,
            "total_interactions": self.interaction_count
        }

# Enhanced components
class EmotionalState(Enum):
    CALM = "calm"
    AGITATED = "agitated"
    PASSIONATE = "passionate"
    DEFENSIVE = "defensive"
    AGGRESSIVE = "aggressive"

class DebatePhase(Enum):
    OPENING = "opening"
    EXPLORATION = "exploration"
    CONFRONTATION = "confrontation"
    RESOLUTION = "resolution"
    REFLECTION = "reflection"

@dataclass
class PersonalityDynamics:
    base_emotional_state: EmotionalState
    trigger_sensitivity: float  # 0-1: how easily triggered by opposing views
    adaptation_rate: float     # 0-1: how quickly agent adapts its strategy
    confidence_level: float    # 0-1: impacts argument strength
    learning_coefficient: float # 0-1: ability to learn from debate history

    def calculate_emotional_impact(self, message_content: str, trigger_words: List[str]) -> float:
        """Calculate emotional impact of a message based on trigger words and sensitivity"""
        trigger_count = sum(word in message_content.lower() for word in trigger_words)
        return min(1.0, trigger_count * self.trigger_sensitivity)

@dataclass
class ArgumentStructure:
    premises: List[str]
    conclusion: str
    supporting_evidence: List[str]
    counter_arguments: List[str]
    fallback_positions: List[str]
    
    def strengthen_argument(self, confidence: float) -> str:
        """Generate stronger version of argument based on confidence"""
        strength_modifiers = {
            0.8: ["Clearly", "Obviously", "Without doubt"],
            0.6: ["Evidence suggests", "Research shows", "Studies indicate"],
            0.4: ["One could argue", "It appears that", "Consider that"]
        }
        
        confidence_tier = max(k for k in strength_modifiers.keys() if confidence >= k)
        modifier = random.choice(strength_modifiers[confidence_tier])
        
        return f"{modifier}, {self.conclusion} because {random.choice(self.premises)}."

class DebateAnalytics:
    def __init__(self):
        self.argument_effectiveness = defaultdict(list)  # Track effectiveness of different arguments
        self.emotional_trajectories = defaultdict(list)  # Track emotional states over time
        self.strategy_adaptations = defaultdict(list)   # Track how strategies evolve
        self.interaction_patterns = defaultdict(int)    # Track patterns in debate flow
        
    def analyze_debate_dynamics(self, messages: List[Message]) -> Dict[str, Any]:
        """Analyze debate patterns and dynamics"""
        return {
            "emotional_volatility": self._calculate_emotional_volatility(messages),
            "argument_coherence": self._measure_argument_coherence(messages),
            "strategy_evolution": self._track_strategy_evolution(messages),
            "interaction_flow": self._analyze_interaction_patterns(messages)
        }
    
    def _calculate_emotional_volatility(self, messages: List[Message]) -> float:
        """Calculate emotional state changes over time"""
        emotional_states = [msg.metadata.get("emotional_state", 0.5) for msg in messages]
        return np.std(emotional_states) if emotional_states else 0.0
    
    def _measure_argument_coherence(self, messages: List[Message]) -> float:
        """Measure how well arguments flow and connect"""
        # Placeholder implementation
        return 0.7
    
    def _track_strategy_evolution(self, messages: List[Message]) -> Dict[str, List[float]]:
        """Track how debate strategies evolve over time"""
        # Placeholder implementation
        return {"strategy_shifts": [0.5, 0.6, 0.7]}
    
    def _analyze_interaction_patterns(self, messages: List[Message]) -> Dict[str, int]:
        """Analyze patterns in how agents interact"""
        # Placeholder implementation
        return {"exchanges": len(messages)}

class DebateEngine:
    """Base debate engine implementation"""

    def __init__(self, config: AppConfig, client: "AIClient"):
        self.config = config
        self.client = client
        self.conversation: List[Message] = []
        self.metrics = DebateMetrics()
        self.status = DebateStatus.NOT_STARTED
        self.current_agent_index = 0
        self.error_count = 0
        self.max_errors = 3
        self._initialize_conversation()

    def _initialize_conversation(self):
        """Initialize conversation with system prompts"""
        for agent in self.config.agents.values():
            self.conversation.append(
                Message(
                    role="system",
                    content=self._generate_agent_prompt(agent),
                    model=agent.model,
                    stance=StanceType(agent.stance),
                    metadata={"agent_name": agent.name},
                )
            )

    def _generate_agent_prompt(self, agent) -> str:
        """Generate agent-specific prompt"""
        return f"You are {agent.name} with {agent.stance} stance."

    def add_user_message(self, message_content: str):
        """Adds a user message to the conversation history."""
        self.conversation.append(
            Message(role="user", content=message_content, model="", stance=None)
        )
        
    def _serialize_message(self, message: Message) -> dict:
        """Helper method to safely serialize message objects"""
        return {
            "role": message.role,
            "content": message.content,
            "model": message.model,
            "timestamp": message.timestamp,
            "stance": message.stance.value if isinstance(message.stance, StanceType) else message.stance,
            "metadata": message.metadata
        }

    def _select_next_agent(self):
        """simple turn-based agent selection"""
        agent_names = list(self.config.agents.keys())
        next_agent_index = self.current_agent_index % len(agent_names)
        self.current_agent_index += 1
        return agent_names[next_agent_index]

    def generate_responses(self, num_turns: int = 1) -> List[str]:
        """Basic response generation -- overridden by EnhancedDebateEngine"""
        responses = []

        for _ in range(num_turns):
            agent_name = self._select_next_agent()
            # Use the new serialization method
            messages = [self._serialize_message(m) for m in self.conversation]
            
            response = self.client.generate_response(
                messages, self.config.agents[agent_name].model
            )
            
            self.conversation.append(
                Message(
                    role="assistant",
                    content=response,
                    model=self.config.agents[agent_name].model,
                    stance=StanceType(self.config.agents[agent_name].stance),
                    metadata={"agent_name": agent_name}
                )
            )
            responses.append(response)
        return responses

    def get_debate_summary(self) -> str:
        """Placeholder for generating a debate summary."""
        return "Debate summary not yet implemented."

    def _analyze_agent_performances(self) -> Dict[str, Any]:
        """Placeholder for analyzing agent performance."""
        return {"agent_performances": "Agent performance analysis not yet implemented."}

    def _analyze_debate_progression(self) -> Dict[str, Any]:
        """Placeholder for analyzing debate progression."""
        return {"debate_progression": "Debate progression analysis not yet implemented."}

    def _calculate_emotional_intensity(self, messages: List[Message]) -> float:
        """Placeholder for calculate emotional intensity"""
        return 0.0

    def _evaluate_argument_strength(self, messages: List[Message]) -> float:
        """Placeholder for evaluate argument strength"""
        return 0.0

    def _track_topic_evolution(self, messages: List[Message]) -> List[str]:
        """Placeholder for track topic evolution"""
        return []

    def _generate_premises(self, belief: str) -> List[str]:
        """Placeholder for generate premises"""
        return [f"Premise supporting {belief}"]

    def _generate_evidence(self, belief: str) -> List[str]:
        """Placeholder for generate evidence"""
        return [f"Evidence supporting {belief}"]

    def _generate_fallbacks(self, belief: str) -> List[str]:
        """Placeholder for generate fallbacks"""
        return [f"Fallback position for {belief}"]

    def _evaluate_response_effectiveness(self, response: str) -> float:
        """Placeholder for evaluate response effectiveness"""
        return 0.0

    def _calculate_emotional_adjustment(
        self, base_state: EmotionalState, intensity: float
    ) -> float:
        """Placeholder for calculate emotional adjustment"""
        return 0.0

    def _calculate_argument_adjustment(
        self, confidence: float, strength: float
    ) -> float:
        """Placeholder for calculate argument adjustment"""
        return 0.0

    def _adapt_rhetoric_style(
        self, primary_style: str, emotional_adjustment: float
    ) -> str:
        """Placeholder for adapt rhetoric style"""
        return "Adapted rhetoric style"

    def _select_argument_structure(
        self, argument_list: List[ArgumentStructure], adjustment: float
    ) -> ArgumentStructure:
        """Placeholder for select argument structure"""
        return argument_list[0]

    def _determine_strategic_focus(self, phase: DebatePhase) -> str:
        """Placeholder for determine strategic focus"""
        return "Strategic focus"

    def _generate_opening(self, rhetoric: str, phase: DebatePhase) -> str:
        """Placeholder for generate opening"""
        return "Opening statement"

    def _generate_supporting_points(
        self, argument: ArgumentStructure, focus: str
    ) -> str:
        """Placeholder for generate supporting points"""
        return "Supporting points"

    def _generate_conclusion(self, rhetoric: str, phase: DebatePhase) -> str:
        """Placeholder for generate conclusion"""
        return "Conclusion"

class EnhancedDebateEngine(DebateEngine):
    def __init__(self, config: 'AppConfig', client: 'AIClient'):
        super().__init__(config, client)
        self.analytics = DebateAnalytics()
        self.current_phase = DebatePhase.OPENING
        self.personality_dynamics = self._initialize_personality_dynamics()
        self.argument_registry = self._build_argument_registry()
        
    def _initialize_personality_dynamics(self) -> Dict[str, PersonalityDynamics]:
        """Initialize personality dynamics for each agent"""
        return {
            agent_name: PersonalityDynamics(
                base_emotional_state=random.choice(list(EmotionalState)),
                trigger_sensitivity=random.uniform(0.3, 0.8),
                adaptation_rate=random.uniform(0.2, 0.6),
                confidence_level=random.uniform(0.4, 0.9),
                learning_coefficient=random.uniform(0.3, 0.7)
            )
            for agent_name in self.config.agents.keys()
        }
    
    def _build_argument_registry(self) -> Dict[str, List[ArgumentStructure]]:
        """Build a registry of argument structures for each agent"""
        registry = {}
        for agent_name, agent_config in self.config.agents.items():
            registry[agent_name] = []
            for belief in agent_config.core_beliefs:
                # Find relevant counter-arguments
                relevant_counter_args = []
                for key in agent_config.counter_arguments:
                    if key.lower() in belief.lower():  # Check if key is in belief
                        relevant_counter_args.extend(agent_config.counter_arguments[key])

                registry[agent_name].append(
                    ArgumentStructure(
                        premises=self._generate_premises(belief),
                        conclusion=belief,
                        supporting_evidence=self._generate_evidence(belief),
                        counter_arguments=relevant_counter_args,  # Use found counter-args
                        fallback_positions=self._generate_fallbacks(belief),
                    )
                )
        return registry

    def _generate_premises(self, belief: str) -> List[str]:
        """Generate supporting premises for a belief"""
        # Placeholder implementation
        return [f"Support for {belief}", f"Evidence for {belief}"]

    def _generate_evidence(self, belief: str) -> List[str]:
        """Generate evidence supporting a belief"""
        # Placeholder implementation
        return [f"Evidence A for {belief}", f"Evidence B for {belief}"]

    def _generate_fallbacks(self, belief: str) -> List[str]:
        """Generate fallback positions for a belief"""
        # Placeholder implementation
        return [f"Fallback 1 for {belief}", f"Fallback 2 for {belief}"]

    def generate_responses(self, num_turns: int = 1) -> List[str]:
        """Enhanced response generation with dynamic adaptation"""
        responses = []
        for _ in range(num_turns):
            agent_name = list(self.config.agents.keys())[self.current_agent_index]
            agent_config = self.config.agents[agent_name]
            personality = self.personality_dynamics[agent_name]
            
            # Analyze debate context
            debate_context = self._analyze_debate_context()
            
            # Adapt strategy based on context
            adapted_strategy = self._adapt_debate_strategy(
                agent_config,
                personality,
                debate_context
            )
            
            # Generate response using adapted strategy
            response = self._generate_strategic_response(
                agent_name,
                adapted_strategy,
                debate_context
            )
            
            # Update analytics and state
            self._update_debate_state(response, agent_name, personality)
            responses.append(response)
            
            # Update agent index
            self.current_agent_index = (self.current_agent_index + 1) % len(self.config.agents)
            
        return responses

    def _analyze_debate_context(self) -> Dict[str, Any]:
        """Analyze current debate context for strategic planning"""
        recent_messages = self.conversation[-3:]
        return {
            "phase": self.current_phase,
            "emotional_intensity": 0.5,  # Placeholder implementation
            "argument_strength": 0.7,    # Placeholder implementation
            "topic_evolution": {"current_focus": "main_topic"}  # Placeholder
        }

    def _adapt_debate_strategy(
        self,
        agent_config: AgentConfig,  # Update type hint to AgentConfig
        personality: PersonalityDynamics,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt debate strategy based on context and personality"""
        # Safely get arguments from registry, fallback to empty list if not found
        available_arguments = self.argument_registry.get(agent_config.name, [])
        
        # Create a default argument if none exist
        if not available_arguments:
            default_argument = ArgumentStructure(
                premises=[f"Default premise for {agent_config.name}"],
                conclusion=f"Default position for {agent_config.name}",
                supporting_evidence=[],
                counter_arguments=[],
                fallback_positions=[]
            )
            available_arguments = [default_argument]
            # Add to registry for future use
            self.argument_registry[agent_config.name] = available_arguments

        return {
            "rhetoric_style": agent_config.rhetoric.primary_style,
            "argument_structure": random.choice(available_arguments),
            "emotional_tone": 0.7,
            "strategic_focus": context["phase"]
        }


    def _generate_strategic_response(
        self,
        agent_name: str,
        strategy: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate response using adapted strategy"""
        argument = strategy["argument_structure"]
        return argument.strengthen_argument(strategy["emotional_tone"])

    def _update_debate_state(self, response: str, agent_name: str, personality: PersonalityDynamics):
        """Update debate state with new response"""
        self.analytics.argument_effectiveness[agent_name].append(0.7)  # Placeholder
        self.analytics.emotional_trajectories[agent_name].append(
            personality.calculate_emotional_impact(response, 
                self.config.agents[agent_name].rhetoric.trigger_phrases)
        )
        self._progress_debate_phase()

    def _progress_debate_phase(self):
        """Progress debate through phases based on context"""
        phase_transitions = {
            DebatePhase.OPENING: (3, DebatePhase.EXPLORATION),
            DebatePhase.EXPLORATION: (5, DebatePhase.CONFRONTATION),
            DebatePhase.CONFRONTATION: (8, DebatePhase.RESOLUTION),
            DebatePhase.RESOLUTION: (10, DebatePhase.REFLECTION)
        }
        
        current_messages = len([m for m in self.conversation if m.role == "assistant"])
        for current_phase, (threshold, next_phase) in phase_transitions.items():
            if self.current_phase == current_phase and current_messages >= threshold:
                self.current_phase = next_phase
                break

    def get_debate_analysis(self) -> Dict[str, Any]:
        """Get comprehensive debate analysis"""
        return {
            "dynamics": self.analytics.analyze_debate_dynamics(self.conversation),
            "agent_performances": {
                agent: len(self.analytics.argument_effectiveness[agent])
                for agent in self.config.agents
            },
            "debate_progression": {
                "current_phase": self.current_phase.value,
                "messages_count": len(self.conversation),
                "emotional_trajectory": dict(self.analytics.emotional_trajectories)
            }
        }