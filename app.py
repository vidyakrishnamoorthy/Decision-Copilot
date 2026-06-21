import secrets

from flask import Flask, redirect, render_template_string, request, session, url_for


app = Flask(__name__)
app.secret_key = "decision-copilot-dev"


PAGE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Decision Copilot</title>
    <style>
      :root {
        color-scheme: dark;
        --bg: #070b18;
        --panel: rgba(13, 20, 38, 0.86);
        --text: #f6f7fb;
        --muted: #b8c2d8;
        --border: rgba(190, 205, 235, 0.22);
        --accent: #7dd3fc;
        --accent-dark: #38bdf8;
        --bubble: #2563eb;
        --shadow: 0 22px 52px rgba(0, 0, 0, 0.38);
      }

      * {
        box-sizing: border-box;
      }

      body {
        position: relative;
        overflow-x: hidden;
        margin: 0;
        min-height: 100vh;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background:
          radial-gradient(circle at 78% 16%, rgba(255, 255, 255, 0.16) 0 2.6rem, transparent 2.7rem),
          radial-gradient(circle at 80% 14%, #fff8d8 0 2.25rem, #f8e9a8 2.3rem 2.7rem, transparent 2.8rem),
          radial-gradient(circle at 18% 20%, rgba(125, 211, 252, 0.16), transparent 24rem),
          linear-gradient(180deg, #030712 0%, #0b1022 48%, #111827 100%);
        color: var(--text);
      }

      body::before,
      body::after {
        position: fixed;
        inset: 0;
        z-index: -1;
        pointer-events: none;
        content: "";
      }

      body::before {
        background-image:
          radial-gradient(circle, rgba(255, 255, 255, 0.96) 0 1px, transparent 1.5px),
          radial-gradient(circle, rgba(191, 219, 254, 0.86) 0 1px, transparent 1.6px),
          radial-gradient(circle, rgba(255, 255, 255, 0.62) 0 1px, transparent 1.4px);
        background-position: 12px 20px, 72px 92px, 136px 46px;
        background-size: 150px 130px, 210px 180px, 270px 220px;
        opacity: 0.9;
      }

      body::after {
        background:
          radial-gradient(circle at 12% 88%, rgba(15, 23, 42, 0.95) 0 4rem, transparent 4.1rem),
          radial-gradient(circle at 29% 92%, rgba(15, 23, 42, 0.9) 0 5.5rem, transparent 5.6rem),
          radial-gradient(circle at 58% 96%, rgba(15, 23, 42, 0.9) 0 7rem, transparent 7.1rem),
          radial-gradient(circle at 84% 90%, rgba(15, 23, 42, 0.88) 0 5rem, transparent 5.1rem);
        opacity: 0.75;
      }

      main {
        position: relative;
        z-index: 1;
        width: min(760px, calc(100% - 32px));
        margin: 0 auto;
        padding: 56px 0;
      }

      h1 {
        margin: 0 0 8px;
        font-size: 42px;
        line-height: 1.1;
        letter-spacing: 0;
      }

      .subtitle {
        margin: 0 0 28px;
        color: var(--muted);
        font-size: 17px;
      }

      form {
        display: grid;
        gap: 14px;
        padding: 24px;
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 8px;
        box-shadow: var(--shadow);
        backdrop-filter: blur(16px);
      }

      .actions {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }

      label {
        font-weight: 650;
      }

      textarea {
        width: 100%;
        min-height: 96px;
        resize: vertical;
        padding: 14px 16px;
        border: 1px solid var(--border);
        border-radius: 8px;
        background: rgba(3, 7, 18, 0.62);
        color: var(--text);
        font: inherit;
        line-height: 1.5;
      }

      textarea::placeholder {
        color: #94a3b8;
      }

      textarea:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.14);
        outline: none;
      }

      button {
        justify-self: start;
        min-height: 44px;
        padding: 0 18px;
        border: 0;
        border-radius: 8px;
        background: var(--accent);
        color: #06111f;
        font: inherit;
        font-weight: 700;
        cursor: pointer;
      }

      button:hover {
        background: var(--accent-dark);
      }

      .clear-button {
        border: 1px solid var(--border);
        background: rgba(15, 23, 42, 0.74);
        color: var(--text);
      }

      .clear-button:hover {
        background: rgba(30, 41, 59, 0.9);
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

      .message-row.assistant {
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
    </style>
  </head>
  <body>
    <main>
      <h1>Decision Copilot</h1>
      <p class="subtitle">Enter the decision, question, or tradeoff you want to work through.</p>

      <section class="chat" aria-live="polite" aria-label="Chat messages">
        <div class="message-row assistant">
          <div class="message-bubble assistant">What can I help you decide today?</div>
        </div>
        {% if messages %}
          {% for message in messages %}
            <div class="message-row">
              <div class="message-bubble">{{ message }}</div>
            </div>
          {% endfor %}
        {% endif %}
      </section>

      <form method="post">
        <label for="user_input">Your input</label>
        <input type="hidden" name="submit_token" value="{{ submit_token }}">
        <textarea id="user_input" name="user_input" placeholder="Type your decision here..."></textarea>
        <div class="actions">
          <button type="submit" name="action" value="send">Submit</button>
          <button class="clear-button" type="submit" name="action" value="clear">Clear history</button>
        </div>
      </form>
    </main>
  </body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    messages = session.get("messages", [])
    submit_token = session.get("submit_token")

    if not submit_token:
        submit_token = secrets.token_urlsafe(16)
        session["submit_token"] = submit_token

    if request.method == "POST":
        action = request.form.get("action", "send")
        submitted_token = request.form.get("submit_token", "")
        if action == "clear" and submitted_token == submit_token:
            session.pop("messages", None)
        elif action == "send":
            user_input = request.form.get("user_input", "").strip()
            if user_input and submitted_token == submit_token:
                messages = [*messages, user_input]
                session["messages"] = messages
        session["submit_token"] = secrets.token_urlsafe(16)
        return redirect(url_for("index"))

    return render_template_string(PAGE, messages=messages, submit_token=submit_token)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
