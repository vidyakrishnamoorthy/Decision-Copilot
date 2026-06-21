import html
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


st.set_page_config(page_title="Decision Copilot", page_icon="*", layout="centered")

SYSTEM_PROMPT = """
You are Decision Copilot. The user is at a career crossroads.
Only answer questions about career crossroads, job decisions, role changes,
promotion choices, leaving or staying, switching fields, negotiating offers,
and related career tradeoffs.
If the user asks about anything outside that scope, briefly say you can only
help with career crossroads questions and ask them to refocus on a career
decision.
Do not tell the user what to choose. Do not recommend a decision.
Instead, present the main options with clear pros and cons, note any tradeoffs
or risks, and end by asking whether there are any additional factors they want
to consider.
Keep the tone sympathetic yet professional. Keep responses concise, specific,
and easy to act on.
"""


def add_page_styles():
    st.markdown(
        """
        <style>
          :root {
            color-scheme: dark;
            --panel: rgba(13, 20, 38, 0.86);
            --text: #f6f7fb;
            --muted: #b8c2d8;
            --border: rgba(190, 205, 235, 0.22);
            --accent: #7dd3fc;
            --accent-dark: #38bdf8;
            --bubble: #2563eb;
            --shadow: 0 22px 52px rgba(0, 0, 0, 0.38);
          }

          .stApp {
            background:
              radial-gradient(circle at 78% 16%, rgba(255, 255, 255, 0.16) 0 2.6rem, transparent 2.7rem),
              radial-gradient(circle at 80% 14%, #fff8d8 0 2.25rem, #f8e9a8 2.3rem 2.7rem, transparent 2.8rem),
              radial-gradient(circle at 18% 20%, rgba(125, 211, 252, 0.16), transparent 24rem),
              linear-gradient(180deg, #030712 0%, #0b1022 48%, #111827 100%);
            color: var(--text);
          }

          .stApp::before,
          .stApp::after {
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            content: "";
          }

          .stApp::before {
            background-image:
              radial-gradient(circle, rgba(255, 255, 255, 0.96) 0 1px, transparent 1.5px),
              radial-gradient(circle, rgba(191, 219, 254, 0.86) 0 1px, transparent 1.6px),
              radial-gradient(circle, rgba(255, 255, 255, 0.62) 0 1px, transparent 1.4px);
            background-position: 12px 20px, 72px 92px, 136px 46px;
            background-size: 150px 130px, 210px 180px, 270px 220px;
            opacity: 0.9;
          }

          .stApp::after {
            background:
              radial-gradient(circle at 12% 88%, rgba(15, 23, 42, 0.95) 0 4rem, transparent 4.1rem),
              radial-gradient(circle at 29% 92%, rgba(15, 23, 42, 0.9) 0 5.5rem, transparent 5.6rem),
              radial-gradient(circle at 58% 96%, rgba(15, 23, 42, 0.9) 0 7rem, transparent 7.1rem),
              radial-gradient(circle at 84% 90%, rgba(15, 23, 42, 0.88) 0 5rem, transparent 5.1rem);
            opacity: 0.75;
          }

          .block-container {
            position: relative;
            z-index: 1;
            max-width: 760px;
            padding-top: 56px;
          }

          h1 {
            letter-spacing: 0;
          }

          .subtitle {
            margin: -0.5rem 0 1.75rem;
            color: var(--muted);
            font-size: 17px;
          }

          .chat {
            display: grid;
            gap: 10px;
            margin-bottom: 20px;
            padding: 18px;
            min-height: 96px;
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(16px);
          }

          .message-row {
            display: flex;
            justify-content: flex-end;
          }

          .message-row.assistant,
          .message-row.error {
            justify-content: flex-start;
          }

          .message-bubble {
            max-width: min(80%, 520px);
            padding: 12px 16px;
            background: var(--bubble);
            color: #ffffff;
            border-radius: 18px 18px 4px 18px;
            line-height: 1.45;
            overflow-wrap: anywhere;
            white-space: pre-wrap;
          }

          .message-bubble.assistant {
            background: rgba(226, 232, 240, 0.14);
            border: 1px solid var(--border);
            color: var(--text);
            border-radius: 18px 18px 18px 4px;
          }

          .message-bubble.error {
            background: rgba(127, 29, 29, 0.45);
            border: 1px solid rgba(252, 165, 165, 0.45);
            color: #fee2e2;
            border-radius: 18px 18px 18px 4px;
          }

          div[data-testid="stForm"] {
            padding: 24px;
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(16px);
          }

          .stTextArea textarea {
            min-height: 96px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: rgba(3, 7, 18, 0.62);
            color: var(--text);
          }

          .stTextArea textarea:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(125, 211, 252, 0.14);
          }

          .stButton button,
          .stFormSubmitButton button {
            min-height: 44px;
            border-radius: 8px;
            font-weight: 700;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_chat(messages):
    rows = [
        """
        <div class="message-row assistant">
          <div class="message-bubble assistant">What career crossroads are you facing today? I can help weigh the options.</div>
        </div>
        """
    ]

    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        escaped_message = html.escape(content)
        row_class = "assistant" if role == "assistant" else role
        bubble_class = "assistant" if role == "assistant" else role
        rows.append(
            f"""
            <div class="message-row {row_class}">
              <div class="message-bubble {bubble_class}">{escaped_message}</div>
            </div>
            """
        )

    st.markdown(f'<section class="chat">{"".join(rows)}</section>', unsafe_allow_html=True)


def normalize_messages(messages):
    if not messages:
        return []

    normalized = []
    for message in messages:
        if isinstance(message, str):
            normalized.append({"role": "user", "content": message})
        elif isinstance(message, dict) and "content" in message:
            normalized.append(
                {
                    "role": message.get("role", "user"),
                    "content": str(message.get("content", "")),
                }
            )
    return normalized


def build_gpt_input(messages):
    input_messages = [{"role": "developer", "content": SYSTEM_PROMPT}]
    for message in messages:
        if message["role"] == "error":
            continue
        role = "assistant" if message["role"] == "assistant" else "user"
        input_messages.append({"role": role, "content": message["content"]})
    return input_messages


def get_openai_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    try:
        return st.secrets.get("OPENAI_API_KEY")
    except Exception:
        return None


def get_openai_model():
    model = os.getenv("OPENAI_MODEL")
    if model:
        return model

    try:
        return st.secrets.get("OPENAI_MODEL", "gpt-5.5")
    except Exception:
        return "gpt-5.5"


def ask_gpt(messages):
    api_key = get_openai_api_key()
    if not api_key:
        return {
            "role": "error",
            "content": "Missing OPENAI_API_KEY. Add it to your environment or Streamlit secrets, then restart the app.",
        }

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=get_openai_model(),
            input=build_gpt_input(messages),
        )
        return {"role": "assistant", "content": response.output_text}
    except Exception as exc:
        return {
            "role": "error",
            "content": f"GPT request failed: {exc}",
        }


def rerun_app():
    rerun = getattr(st, "rerun", None)
    if callable(rerun):
        rerun()
        return

    experimental_rerun = getattr(st, "experimental_rerun", None)
    if callable(experimental_rerun):
        experimental_rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []
else:
    st.session_state.messages = normalize_messages(st.session_state.messages)

add_page_styles()

st.title("Decision Copilot")
st.markdown(
    '<p class="subtitle">Enter the decision, question, or tradeoff you want to work through.</p>',
    unsafe_allow_html=True,
)

render_chat(st.session_state.messages)

with st.form("decision_input", clear_on_submit=True):
    user_input = st.text_area("Your input", placeholder="Type your decision here...")
    send, clear = st.columns([1, 1])

    with send:
        submitted = st.form_submit_button("Submit")

    with clear:
        cleared = st.form_submit_button("Clear history")

if submitted:
    cleaned_input = user_input.strip()
    if cleaned_input:
        st.session_state.messages.append({"role": "user", "content": cleaned_input})
        st.session_state.messages.append(ask_gpt(st.session_state.messages))
        rerun_app()

if cleared:
    st.session_state.messages = []
    rerun_app()
