import gradio as gr
from app.ai_agent.agent import run_agent
from app.ai_agent.rag.index import init_collection, index_logs

init_collection()
index_logs()

theme = gr.themes.Base(primary_hue="indigo", neutral_hue="slate").set(
    body_background_fill="#0b0f19",
    body_text_color="#ffffff",
    block_background_fill="#111827",
    block_border_color="#1f2937",
    input_background_fill="#111827",
    input_border_color="#1f2937",
)

css = """
html, body {
    height: 100% !important;
    margin: 0 !important;
}

/* Root container */
.gradio-container {
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    background: #0b0f19 !important;
}

/* Internal wrapper */
.gradio-container > div {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}

/* ChatInterface wrapper */
.gr-chat-interface {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
}

/* Chatbot grows */
.gr-chatbot {
    flex: 1 !important;
    overflow-y: auto !important;
}

/* Input stays at bottom */
.gr-chat-interface .input-row {
    margin-top: auto !important;
}

/* SAFE label removal */
.gr-chatbot label,
.gr-chatbot .label-wrap {
    display: none !important;
    height: 0 !important;
}

/* Messages */
.message.user {
    background-color: #1f2937 !important;
    color: white !important;
}

.message.bot {
    background-color: #0f172a !important;
    color: white !important;
    border: 1px solid #1e293b !important;
}

/* Input */
textarea {
    color: white !important;
}

/* Fix markdown text visibility */
.message.bot pre {
    background-color: #020617 !important;
    color: #e5e7eb !important;
    border-radius: 8px !important;
    padding: 10px !important;
    font-size: 13px !important;
    line-height: 1.5 !important;
    overflow-x: auto !important;
}

/* Inline code */
.message.bot code {
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
}

/* Ensure readable text */
.message.bot p,
.message.bot li,
.message.bot span {
    color: #e5e7eb !important;
}

/* Fix faint text */
.message.bot * {
    opacity: 1 !important;
}

footer {
    display: none !important;
}
"""


def run_agent_with_token(message, history, request: gr.Request):
    try:
        print("here we go again!")
        token = request.query_params.get("token")

        if not token:
            return "Missing authentication token"

        return run_agent(message=message, history=history, token=token)

    except Exception as e:
        print(f"Gradio error: {e}")
        return f"UI error: {str(e)}"


with gr.Blocks(theme=theme, css=css) as grad_ui:
    gr.ChatInterface(
        fn=run_agent_with_token,
        chatbot=gr.Chatbot(
            label=None,
            show_label=False,
            height=900
        ),
        textbox=gr.Textbox(
            placeholder="Type your message....",
            container=True
        ),
    )

grad_ui.launch(server_port=7860)