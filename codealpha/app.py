from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from faq_chatbot import build_default_chatbot


CHATBOT = build_default_chatbot()


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LearnMate FAQ Chatbot</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #172026;
      --muted: #5e6a71;
      --line: #d9dee2;
      --page: #f4f6f8;
      --panel: #ffffff;
      --primary: #28666e;
      --primary-dark: #17484f;
      --accent: #c46536;
      --bot: #eef6f5;
      --user: #172026;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--page);
      color: var(--ink);
    }

    .app {
      display: grid;
      grid-template-columns: minmax(220px, 320px) minmax(0, 1fr);
      min-height: 100vh;
    }

    .sidebar {
      background: #172026;
      color: white;
      padding: 28px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 28px;
    }

    h1 {
      margin: 0 0 12px;
      font-size: clamp(1.8rem, 4vw, 3.1rem);
      line-height: 1.02;
      letter-spacing: 0;
    }

    .topic {
      margin: 0;
      max-width: 28rem;
      color: #b7c4c9;
      line-height: 1.55;
    }

    .examples {
      display: grid;
      gap: 10px;
    }

    .examples button,
    .send {
      border: 0;
      cursor: pointer;
      font: inherit;
    }

    .examples button {
      min-height: 42px;
      border-radius: 8px;
      background: #243138;
      color: white;
      text-align: left;
      padding: 10px 12px;
    }

    .examples button:hover {
      background: #304149;
    }

    main {
      display: grid;
      place-items: center;
      padding: 28px;
    }

    .chat {
      width: min(920px, 100%);
      height: min(760px, calc(100vh - 56px));
      min-height: 520px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      display: grid;
      grid-template-rows: auto 1fr auto;
      overflow: hidden;
      box-shadow: 0 20px 70px rgb(23 32 38 / 12%);
    }

    .chat-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
    }

    .chat-title {
      margin: 0;
      font-size: 1rem;
      font-weight: 800;
    }

    .status {
      color: var(--muted);
      font-size: 0.86rem;
      white-space: nowrap;
    }

    .messages {
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 14px;
      background:
        linear-gradient(#ffffff, #ffffff) padding-box,
        repeating-linear-gradient(90deg, #f7f9fa 0 1px, transparent 1px 72px);
    }

    .message {
      max-width: min(72ch, 86%);
      border-radius: 8px;
      padding: 12px 14px;
      line-height: 1.48;
      overflow-wrap: anywhere;
    }

    .message.bot {
      align-self: flex-start;
      background: var(--bot);
      border: 1px solid #d6e9e7;
    }

    .message.user {
      align-self: flex-end;
      background: var(--user);
      color: white;
    }

    .meta {
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.82rem;
    }

    .composer {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      padding: 14px;
      border-top: 1px solid var(--line);
      background: white;
    }

    input {
      min-width: 0;
      height: 46px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 0 14px;
      font: inherit;
      color: var(--ink);
    }

    input:focus {
      border-color: var(--primary);
      outline: 3px solid rgb(40 102 110 / 18%);
    }

    .send {
      min-width: 94px;
      height: 46px;
      border-radius: 8px;
      background: var(--primary);
      color: white;
      font-weight: 800;
    }

    .send:hover {
      background: var(--primary-dark);
    }

    .send:disabled {
      cursor: wait;
      opacity: 0.72;
    }

    @media (max-width: 760px) {
      .app {
        grid-template-columns: 1fr;
      }

      .sidebar {
        padding: 22px;
      }

      .examples {
        grid-template-columns: 1fr 1fr;
      }

      main {
        padding: 14px;
        place-items: stretch;
      }

      .chat {
        min-height: 560px;
        height: calc(100vh - 28px);
      }

      .message {
        max-width: 94%;
      }
    }

    @media (max-width: 480px) {
      .examples {
        grid-template-columns: 1fr;
      }

      .composer {
        grid-template-columns: 1fr;
      }

      .send {
        width: 100%;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div>
        <h1>LearnMate FAQ Chatbot</h1>
        <p class="topic">Ask about accounts, course access, payments, certificates, support, and subscriptions.</p>
      </div>
      <div class="examples" aria-label="Example questions">
        <button type="button">How do I reset my password?</button>
        <button type="button">Can I get a refund?</button>
        <button type="button">How do I download my certificate?</button>
        <button type="button">Are lessons live?</button>
      </div>
    </aside>
    <main>
      <section class="chat" aria-label="FAQ chatbot">
        <header class="chat-header">
          <p class="chat-title">Chat</p>
          <span class="status" id="status">Ready</span>
        </header>
        <div class="messages" id="messages" aria-live="polite">
          <article class="message bot">Hi. I can answer LearnMate FAQ questions.</article>
        </div>
        <form class="composer" id="form">
          <input id="question" name="question" autocomplete="off" placeholder="Type your question" required>
          <button class="send" id="send" type="submit">Send</button>
        </form>
      </section>
    </main>
  </div>

  <script>
    const form = document.querySelector("#form");
    const input = document.querySelector("#question");
    const messages = document.querySelector("#messages");
    const status = document.querySelector("#status");
    const send = document.querySelector("#send");

    function addMessage(text, sender, meta = "") {
      const message = document.createElement("article");
      message.className = `message ${sender}`;
      message.textContent = text;
      if (meta) {
        const details = document.createElement("div");
        details.className = "meta";
        details.textContent = meta;
        message.appendChild(details);
      }
      messages.appendChild(message);
      messages.scrollTop = messages.scrollHeight;
    }

    async function ask(question) {
      addMessage(question, "user");
      input.value = "";
      send.disabled = true;
      status.textContent = "Matching";

      try {
        const response = await fetch("/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question })
        });
        const result = await response.json();
        const meta = result.matched_question
          ? `Matched: ${result.matched_question} | similarity ${result.score}`
          : `No close match | similarity ${result.score}`;
        addMessage(result.answer, "bot", meta);
      } catch (error) {
        addMessage("The chatbot server did not respond. Please try again.", "bot");
      } finally {
        send.disabled = false;
        status.textContent = "Ready";
        input.focus();
      }
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const question = input.value.trim();
      if (question) ask(question);
    });

    document.querySelectorAll(".examples button").forEach((button) => {
      button.addEventListener("click", () => ask(button.textContent));
    });
  </script>
</body>
</html>
"""


class FAQRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(INDEX_HTML)
            return
        if path == "/health":
            self._send_json({"ok": True})
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/ask":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        body_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(body_length)
        try:
            payload = json.loads(body.decode("utf-8"))
            question = str(payload.get("question", "")).strip()
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json({"error": "Invalid JSON request."}, HTTPStatus.BAD_REQUEST)
            return

        if not question:
            self._send_json({"error": "Question is required."}, HTTPStatus.BAD_REQUEST)
            return

        self._send_json(CHATBOT.ask(question))

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_html(self, content: str) -> None:
        encoded = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LearnMate FAQ chatbot web UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), FAQRequestHandler)
    print(f"LearnMate FAQ chatbot running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
