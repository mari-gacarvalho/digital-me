import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# GPT-5.4 Mini
OPENAI_INPUT_COST_PER_M = 0.75
OPENAI_OUTPUT_COST_PER_M = 4.50

# Claude Haiku 5.5
ANTHROPIC_INPUT_COST_PER_M = 0.10
ANTHROPIC_OUTPUT_COST_PER_M = 0.50


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        return {"status": "success", "message": text}
    else:
        return {"status": "error", "message": response.text}


def record_user_details(email, name="Name not provided", notes="not provided"):
    send_telegram_message(
        f"Recording interest from {name} with email {email} and notes {notes}"
    )
    return {"recorded": "ok"}


def record_unknown_question(question):
    send_telegram_message(f"Recording {question} asked that I couldn't answer")
    return {"recorded": "ok"}


record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user",
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it",
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context",
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered",
            },
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]

tool_map = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
}


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        tool = tool_map.get(tool_name)
        result = tool(**arguments) if tool else "Unknown tool: " + tool_name
        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
        )
    return results

def calculate_cost(
    input_tokens,
    output_tokens,
    input_cost_per_m,
    output_cost_per_m,
):
    input_cost = (input_tokens / 1_000_000) * input_cost_per_m
    output_cost = (output_tokens / 1_000_000) * output_cost_per_m

    return input_cost + output_cost

def record_usage_metrics(
    latency_seconds,
    openai_prompt_tokens,
    openai_completion_tokens,
    anthropic_input_tokens,
    anthropic_output_tokens,
    evaluator_accepted,
    regenerated=False,
):
    openai_cost = calculate_cost(
        openai_prompt_tokens,
        openai_completion_tokens,
        OPENAI_INPUT_COST_PER_M,
        OPENAI_OUTPUT_COST_PER_M,
    )

    anthropic_cost = calculate_cost(
        anthropic_input_tokens,
        anthropic_output_tokens,
        ANTHROPIC_INPUT_COST_PER_M,
        ANTHROPIC_OUTPUT_COST_PER_M,
    )

    total_tokens = (
        openai_prompt_tokens
        + openai_completion_tokens
        + anthropic_input_tokens
        + anthropic_output_tokens
    )

    total_cost = openai_cost + anthropic_cost

    message = (
        "Digital Me usage\n\n"
        f"Latency: {latency_seconds:.2f}s\n\n"

        "OpenAI\n"
        f"Input: {openai_prompt_tokens} tokens\n"
        f"Output: {openai_completion_tokens} tokens\n"
        f"Cost: ${openai_cost:.6f}\n\n"

        "Anthropic Evaluator\n"
        f"Input: {anthropic_input_tokens} tokens\n"
        f"Output: {anthropic_output_tokens} tokens\n"
        f"Cost: ${anthropic_cost:.6f}\n\n"

        "Total\n"
        f"Tokens: {total_tokens}\n"
        f"Cost: ${total_cost:.6f}\n\n"

        f"Evaluator accepted: {evaluator_accepted}\n"
        f"Regenerated: {regenerated}"
    )

    return send_telegram_message(message)