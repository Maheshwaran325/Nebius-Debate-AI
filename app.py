# import streamlit as st
# from config import AppConfig
# from api_client import AIClient
# from debate_engine import EnhancedDebateEngine, DebatePhase, EmotionalState
# import time

# def init_session_state():
#     if 'debate_engine' not in st.session_state:
#         st.session_state.debate_started = False
#         st.session_state.turn_count = 0
#         st.session_state.auto_scroll = True
#         st.session_state.current_agent_index = 0
#         st.session_state.debate_engine = None

#     if 'api_key' not in st.session_state:
#         st.session_state.api_key = st.secrets.get("NEBIUS_API_KEY", "")

# def render_message(message, agent_config=None):
#     is_user = message.role == "user"

#     if is_user:
#         with st.container():
#             col1, col2 = st.columns([1, 12])
#             with col1:
#                 st.write("👤")
#             with col2:
#                 st.write("You")
#                 st.text_area("User Input", message.content, height=100, disabled=True,
#                             label_visibility="collapsed")
#     else:
#         if st.session_state.debate_engine and message.role == "assistant":
#             # Find the agent using the metadata instead of model
#             agent_name = message.metadata.get('agent_name')
#             agent = st.session_state.config.agents.get(agent_name)
            
#             if agent:
#                 with st.container():
#                     col1, col2 = st.columns([1, 12])
#                     with col1:
#                         st.write(agent.emoji)
#                     with col2:
#                         st.write(f"{agent.name}")
#                         # Simpler message display without custom CSS
#                         st.text_area(
#                             label="",
#                             value=message.content,
#                             height=100,
#                             disabled=True,
#                             label_visibility="collapsed"
#                         )

# def render_debate_stats():
#     st.sidebar.markdown("### Debate Statistics")
    
#     if st.session_state.debate_engine:
#         # Create three columns for metrics
#         col1, col2, col3 = st.sidebar.columns(3)
        
#         with col1:
#             st.metric("Turns", st.session_state.turn_count)
#         with col2:
#             message_count = sum(1 for m in st.session_state.debate_engine.conversation if m.role != "system")
#             st.metric("Messages", message_count)
#         with col3:
#             current_phase = st.session_state.debate_engine.current_phase.value
#             st.metric("Phase", current_phase.title())
            
#         # Add debate analysis
#         if hasattr(st.session_state.debate_engine, 'get_debate_analysis'):
#             analysis = st.session_state.debate_engine.get_debate_analysis()
            
#             # Show emotional trajectory
#             st.sidebar.markdown("### Emotional Trajectory")
#             for agent, trajectory in analysis['debate_progression']['emotional_trajectory'].items():
#                 if trajectory:
#                     st.sidebar.line_chart(trajectory[-5:])  # Show last 5 emotional states
                    
#             # Show argument effectiveness
#             st.sidebar.markdown("### Agent Performance")
#             performances = analysis['agent_performances']
#             st.sidebar.bar_chart(performances)

#     st.sidebar.markdown("---")
#     st.sidebar.markdown("### Settings")
#     st.session_state.auto_scroll = st.sidebar.checkbox("Auto-scroll to latest", value=st.session_state.get("auto_scroll", True))

# def main():
#     st.set_page_config(
#         page_title="AI Debate Arena",
#         page_icon="🤖",
#         layout="wide",
#         initial_sidebar_state="expanded"
#     )

#     # Custom CSS with enhanced styling
#     st.markdown("""
#         <style>
#         div[data-testid="stButton"] > button:first-child {
#             background-color: #0099ff;
#             color: white;
#             width: 100%;
#         }
#         </style>
#     """, unsafe_allow_html=True)

#     init_session_state()

#     # Enhanced header with debate phase indicator
#     st.markdown("""
#         <div style='text-align: center; 
#                     padding: 2em; 
#                     background: linear-gradient(90deg, #4285F4, #34A853);
#                     border-radius: 10px;
#                     margin-bottom: 2em;
#                     color: white;'>
#             <h1 style='margin-bottom: 0.5em;'>AI Debate Arena</h1>
#             <p style='font-size: 1.2em; opacity: 0.9;'>
#                 Watch two AI agents engage in an intellectual discourse
#             </p>
#         </div>
#     """, unsafe_allow_html=True)

#     conversation_col = st.columns([1])[0]

#     with conversation_col:
#         with st.sidebar:
#             st.markdown("### Enter Your API Key")
#             api_key_input = st.text_input("Nebius API Key", type="password", value=st.session_state.api_key, key="api_key_input")
#             st.session_state.api_key = api_key_input

#             if not st.session_state.debate_started:
#                 with st.form("debate_input", clear_on_submit=True):
#                     st.markdown("### Start a New Debate")
#                     user_input = st.text_area(
#                         "What would you like the AI agents to debate?",
#                         placeholder="Enter your question or topic for debate...",
#                         height=150,
#                         key="initial_user_input" 
#                     )
#                     submit_button = st.form_submit_button("Begin Debate")

#                     if submit_button and user_input:
#                         if not st.session_state.api_key and not st.secrets.get("NEBIUS_API_KEY"):
#                             st.error("Please enter a Nebius API key or set the NEBIUS_API_KEY secret.")
#                             return

#                         config = AppConfig(api_key=st.session_state.api_key or st.secrets.get("NEBIUS_API_KEY"))
#                         config.agents = config.agents
#                         client = AIClient(config)
#                         # Use EnhancedDebateEngine instead of DebateEngine
#                         st.session_state.debate_engine = EnhancedDebateEngine(config, client)
#                         st.session_state.config = config

#                         st.session_state.debate_engine.add_user_message(user_input)
#                         st.session_state.debate_started = True
#                         st.session_state.turn_count = 0
                        
#                         with st.spinner("🤔 Agents are thinking..."):
#                             st.session_state.debate_engine.generate_responses()
#                         st.rerun()

#         with st.sidebar:
#             if st.session_state.debate_started:
#                 next_turn_button = st.button(
#                     "Generate Next Turn",
#                     help="Click to generate the next round of responses",
#                     key="next_turn_button"
#                 )

#                 if next_turn_button:
#                     with st.spinner("🤔 Agents are thinking..."):
#                         st.session_state.debate_engine.generate_responses()
#                         st.session_state.turn_count += 1
#                     st.success("Turn generated successfully!")

#                     if st.session_state.auto_scroll:
#                         st.query_params["scroll_to_bottom"] = str(time.time())

#     if st.session_state.debate_started:
#         with conversation_col:
#             # Show current debate phase
#             current_phase = st.session_state.debate_engine.current_phase.value
#             st.markdown(f"**Current Phase:** {current_phase.title()}")
            
#             st.markdown("### Debate History")
#             for message in st.session_state.debate_engine.conversation:
#                 if message.role != "system":    
#                     render_message(message)

#     render_debate_stats()

# if __name__ == "__main__":
#     main()

import streamlit as st
from config import AppConfig
from api_client import AIClient
from debate_engine import DebateEngine
import time

def init_session_state():
    if 'debate_engine' not in st.session_state:
        st.session_state.debate_started = False
        st.session_state.turn_count = 0
        st.session_state.auto_scroll = True
        st.session_state.current_agent_index = 0
        st.session_state.debate_engine = None
    
    # Initialize api_key with previously saved value if it exists
    if 'api_key' not in st.session_state:
        st.session_state.api_key = st.secrets.get("NEBIUS_API_KEY", "")

def render_message(message, agent_config=None):
    is_user = message.role == "user"

    if is_user:
        with st.container():
            col1, col2 = st.columns([1, 12])
            with col1:
                st.write("👤")
            with col2:
                st.write("You")
                st.text_area("User Input", message.content, height=100, disabled=False,
                            label_visibility="collapsed")
    else:
        # Check if debate_engine exists before accessing it.
        if st.session_state.debate_engine:
            agent = next(
                (a for a in st.session_state.config.agents.values() if a.model == message.model),
                None
            )
            if agent:
                with st.container():
                    col1, col2 = st.columns([1, 12])
                    with col1:
                        st.write(agent.emoji)
                    with col2:
                        st.write(f"{agent.name}")
                        st.markdown(f"""
                        <div style='background-color: {agent.color}15;
                                    padding: 1.5em;
                                    border-radius: 12px;
                                    border-left: 5px solid {agent.color};
                                    margin: 10px 0;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.1)'>
                            {message.content}
                        </div>
                        """, unsafe_allow_html=True)

def render_debate_stats():
    st.sidebar.markdown("### Debate Statistics")
    col1, col2 = st.sidebar.columns(2)

    # Check if debate_engine exists before accessing it.
    if st.session_state.debate_engine:
        with col1:
            st.metric("Turns", st.session_state.turn_count)
        with col2:
            message_count = sum(1 for m in st.session_state.debate_engine.conversation if m.role != "system")
            st.metric("Messages", message_count)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Settings")
    st.session_state.auto_scroll = st.sidebar.checkbox("Auto-scroll to latest", value= st.session_state.get("auto_scroll", True))

def main():
    st.set_page_config(
        page_title="AI Debate Arena",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
        <style>
        div[data-testid="stButton"] > button:first-child {
            background-color: #0099ff; /* Blue background */
            color: white;              /* White text */
            border-radius: 20px;      /* Rounded corners */
            height: 3em;
            width: 100%;
        }
        div[data-testid="stButton"] > button:hover {
            background-color: #0077cc; /* Darker blue on hover */
            color: #ffffff;            /* White text on hover*/
        }
        </style>
    """, unsafe_allow_html=True)

    init_session_state()

    # Header with gradient
    st.markdown("""
        <div style='text-align: center; 
                    padding: 2em; 
                    background: linear-gradient(90deg, #4285F4, #34A853);
                    border-radius: 10px;
                    margin-bottom: 2em;
                    color: white;'>
            <h1 style='margin-bottom: 0.5em;'>AI Debate Arena</h1>
            <p style='font-size: 1.2em; opacity: 0.9;'>
                Watch two AI agents engage in an intellectual discourse
            </p>
        </div>
    """, unsafe_allow_html=True)

    conversation_col = st.columns([1])[0] #Keep only conversation column

    with conversation_col:
        with st.sidebar: # Move input elements to sidebar
            # API Key Input
            st.markdown("### Enter Your API Key")
            api_key_input = st.text_input("Nebius API Key", type="password", value=st.session_state.api_key, key="api_key_input")
            if api_key_input:
                st.session_state.api_key = api_key_input

            if not st.session_state.debate_started:
                with st.form("debate_input", clear_on_submit=True):
                    st.markdown("### Start a New Debate")
                    user_input = st.text_area(
                        "What would you like the AI agents to debate?",
                        placeholder="Enter your question or topic for debate...",
                        height=150,
                        key="initial_user_input" 
                    )
                    submit_button = st.form_submit_button("Begin Debate")

                    if submit_button and user_input:
                        # Check for API key *before* starting the debate.
                        if not st.session_state.api_key and not st.secrets.get("NEBIUS_API_KEY"):
                            st.error("Please enter a Nebius API key or set the NEBIUS_API_KEY secret.")
                            return  # Stop execution if no key

                        # Initialize AppConfig and AIClient *after* getting the key.
                        config = AppConfig(api_key=st.session_state.api_key or st.secrets.get("NEBIUS_API_KEY"))
                        config.agents = config.agents #Need this line for creating agent
                        client = AIClient(config)
                        st.session_state.debate_engine = DebateEngine(config, client)
                        st.session_state.config = config #For render message function

                        st.session_state.debate_engine.add_user_message(user_input)
                        st.session_state.debate_started = True
                        st.session_state.turn_count = 0
                        # Add these lines to start the debate immediately
                        with st.spinner("🤔 Agents are thinking..."):
                            st.session_state.debate_engine.generate_responses() # Only one agent responds
                        st.rerun()  # Add this line

        with st.sidebar:
            if st.session_state.debate_started:
                # st.markdown("### Debate Progress")
                # # Add this to give the user a place to enter text *after* the debate starts.
                # user_input = st.text_area(
                #     "Enter a follow-up question or comment for the AI agents:",
                #     placeholder="Enter your question or topic for debate...",
                #     height=150,
                #     key="followup_user_input"

                # )
                # if user_input:
                #     from debate_engine import Message
                #     st.session_state.debate_engine.conversation.append(Message(role="user", content=user_input, model="", stance=""))

                next_turn_button = st.button(
                    "Generate Next Turn",
                    help="Click to generate the next round of responses",
                    key="next_turn_button"
                )

                if next_turn_button:
                    with st.spinner("🤔 Agents are thinking..."):
                        st.session_state.debate_engine.generate_responses() # Only one agent responds
                        st.session_state.turn_count += 1
                    st.success("Turn generated successfully!")


                    if st.session_state.auto_scroll:
                        st.query_params["scroll_to_bottom"] = str(time.time())

    # Display conversation
    if st.session_state.debate_started:
        with conversation_col:
            st.markdown("### Debate History")

            for message in st.session_state.debate_engine.conversation: # Display *all* messages
                if message.role != "system":    
                    render_message(message)

    # Render sidebar stats
    render_debate_stats()

if __name__ == "__main__":
    main()