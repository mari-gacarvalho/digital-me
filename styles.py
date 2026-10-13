"""Styling constants for the Digital Mari Gradio app."""

EXAMPLES = [
    "What are you curious about lately?",
    "How do you approach a messy problem?",
    "What are you building or exploring right now?",
    "What kind of work would you love to do more of?",
]


CSS = """
/* =========================
   DIGITAL MARI — BASE
   ========================= */

:root {
    --paper: #f3efe6;
    --card: #faf8f2;
    --ink: #293330;
    --muted: #747a74;
    --line: #d8d1c4;

    --blue: #486b78;
    --blue-dark: #385762;
    --gold: #aa8756;
}


/* ---------- PAGE ---------- */

html,
body,
gradio-app,
.gradio-container {
    background: var(--paper) !important;
    color: var(--ink) !important;
}
.gradio-container .block,
.gradio-container .form {
    background: transparent !important;
}

body {
    margin: 0 !important;
}

.gradio-container {
    font-family:
        "Avenir Next",
        "Helvetica Neue",
        Arial,
        sans-serif !important;

    max-width: 900px !important;
    margin: 0 auto !important;
    padding: 55px 28px 45px !important;
}


/* Remove Gradio extras */

footer,
.built-with,
.show-api,
.api-docs {
    display: none !important;
}


/* =========================
   TITLE
   ========================= */

.gradio-container h1 {
    font-family:
        Georgia,
        "Times New Roman",
        serif !important;

    font-size: 44px !important;
    font-weight: 400 !important;
    line-height: 1.05 !important;

    letter-spacing: -0.035em !important;

    color: var(--ink) !important;

    margin: 0 0 10px 0 !important;
    padding: 0 !important;

    text-align: left !important;
}


/* Description */

.gradio-container h2,
.gradio-container h3,
.gradio-container .prose {
    color: var(--muted) !important;
}


/* =========================
   CHATBOT
   ========================= */

/*
   Target the Chatbot component itself instead of
   trying to style all of Gradio's internal message
   classes.
*/

.gradio-container .chatbot {
    background: transparent !important;

    border: 0 !important;
    border-top: 1px solid var(--line) !important;
    border-radius: 0 !important;

    box-shadow: none !important;

    height: 420px !important;
    min-height: 420px !important;
    max-height: 420px !important;

    margin-top: 24px !important;
    padding-top: 18px !important;

    overflow-y: auto !important;
}


/* Hide chatbot label */

.chatbot .block-label,
.chatbot > label {
    display: none !important;
}


/* =========================
   MESSAGES
   ========================= */

/*
   Gradio versions differ in their internal class
   names, so only apply safe generic rules here.
*/

.chatbot .message {
    font-family:
        "Avenir Next",
        "Helvetica Neue",
        Arial,
        sans-serif !important;

    font-size: 15px !important;
    line-height: 1.65 !important;

    box-shadow: none !important;
}


/* User bubble */

.chatbot .user {
    background: var(--blue) !important;
    color: white !important;

    border: none !important;
    border-radius: 15px 15px 4px 15px !important;
}


/* Assistant */

.chatbot .bot {
    background: transparent !important;
    color: var(--ink) !important;

    border: none !important;
}


/* Make ALL text inside assistant readable */

.chatbot .bot *,
.chatbot .message.bot *,
.chatbot [data-testid="bot"] * {
    color: var(--ink) !important;
}


/* Links */

.chatbot a {
    color: var(--blue) !important;
}


/* Strong text */

.chatbot strong {
    color: inherit !important;
    font-weight: 600 !important;
}


/* =========================
   INPUT
   ========================= */

.gradio-container textarea {
    font-family:
        "Avenir Next",
        "Helvetica Neue",
        Arial,
        sans-serif !important;

    font-size: 14px !important;

    color: var(--ink) !important;
    background: var(--card) !important;

    border: 1px solid var(--line) !important;
    border-radius: 10px !important;

    min-height: 58px !important;

    padding: 16px !important;

    box-shadow: none !important;
}


.gradio-container textarea:focus {
    border-color: var(--blue) !important;
    outline: none !important;
    box-shadow: none !important;
}


.gradio-container textarea::placeholder {
    color: #969a94 !important;
}


/* =========================
   BUTTONS
   ========================= */

/*
   Reset Gradio buttons first.
*/

.gradio-container button {
    font-family:
        "Avenir Next",
        "Helvetica Neue",
        Arial,
        sans-serif !important;

    box-shadow: none !important;
}


/* Primary / Submit */

.gradio-container button.primary {
    background: var(--blue) !important;
    color: white !important;

    border: 0 !important;
    border-radius: 9px !important;

    font-size: 13px !important;
    font-weight: 500 !important;

    min-height: 48px !important;

    padding: 0 24px !important;
}


.gradio-container button.primary:hover {
    background: var(--blue-dark) !important;
}


/* Secondary buttons:
   Retry / Undo / Clear
*/

.gradio-container button.secondary {
    background: transparent !important;

    color: var(--muted) !important;

    border: 1px solid var(--line) !important;
    border-radius: 8px !important;

    font-size: 12px !important;
    font-weight: 400 !important;

    min-height: 36px !important;

    padding: 7px 12px !important;
}


.gradio-container button.secondary:hover {
    background: var(--card) !important;
    color: var(--blue) !important;

    border-color: var(--blue) !important;
}


/* =========================
   EXAMPLES
   ========================= */

.examples,
.examples-holder,
[data-testid="examples"] {
    background: transparent !important;

    border: 0 !important;

    margin-top: 18px !important;
    padding: 0 !important;
}


.examples table,
.examples-table {
    background: transparent !important;
    border: 0 !important;
}


/* Example pills */

.examples button,
.example,
[data-testid="examples"] button {
    background: transparent !important;

    color: var(--muted) !important;

    border: 1px solid var(--line) !important;
    border-radius: 999px !important;

    font-size: 12px !important;
    font-weight: 400 !important;

    padding: 8px 13px !important;

    min-height: auto !important;

    box-shadow: none !important;
}


.examples button:hover,
.example:hover,
[data-testid="examples"] button:hover {
    background: var(--card) !important;

    color: var(--blue) !important;

    border-color: var(--blue) !important;
}


/* =========================
   SCROLLBAR
   ========================= */

::-webkit-scrollbar {
    width: 7px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: #c8c2b7;
    border-radius: 999px;
}

/* =========================
   MESSAGE FIX
   ========================= */

/* Assistant message */
.chatbot .message.bot,
.chatbot .bot,
.chatbot [data-testid="bot"],
.chatbot [data-testid="bot"] .message {
    background: transparent !important;
    color: var(--ink) !important;
}

/* Everything rendered inside assistant markdown */
.chatbot .message.bot *,
.chatbot .bot *,
.chatbot [data-testid="bot"] *,
.chatbot [data-testid="bot"] .message * {
    color: var(--ink) !important;
    background: transparent !important;
}

/* User message */
.chatbot .message.user,
.chatbot .user,
.chatbot [data-testid="user"],
.chatbot [data-testid="user"] .message {
    background: var(--blue) !important;
    color: #ffffff !important;
}

/* Text inside user bubble */
.chatbot .message.user *,
.chatbot .user *,
.chatbot [data-testid="user"] * {
    color: #ffffff !important;
}

/* Remove Gradio's dark internal chat background */
.chatbot,
.chatbot > div,
.chatbot .wrap,
.chatbot .bubble-wrap,
.chatbot .message-wrap,
.chatbot .message-row {
    background-color: transparent !important;
}


/* =========================
   MOBILE
   ========================= */

@media (max-width: 640px) {

    .gradio-container {
        padding: 36px 18px !important;
    }

    .gradio-container h1 {
        font-size: 36px !important;
    }

    .gradio-container .chatbot {
        height: 360px !important;
        min-height: 360px !important;
        max-height: 360px !important;
    }
}
"""


JS = """
() => {
    document.title = "Digital Mari";

    const focusInput = () => {
        const textareas = document.querySelectorAll("textarea");

        if (textareas.length) {
            textareas[textareas.length - 1].focus();
        }
    };

    setTimeout(focusInput, 400);
}
"""