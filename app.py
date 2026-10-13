from openai import OpenAI
from context import TWIN_SYSTEM_PROMPT
from tools import tools, handle_tool_calls, record_usage_metrics
from styles import CSS, JS, EXAMPLES
from dotenv import load_dotenv
import gradio as gr
from gradio.context import Context
import fastapi.exceptions
from rate_limiter import RateLimiter
from evaluator import evaluate
import time

load_dotenv(override=True)

MODEL_NAME = "gpt-5.4-mini"

openai = OpenAI()

system = [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]
rate_limiter = RateLimiter(max_requests=5, time_window=5)

def chat(message, history):
    started_at = time.perf_counter()

    # Get the client IP from Gradio's request context
    try:
        request = Context.get_context().request

        forwarded_for = request.headers.get("X-Forwarded-For")
        cloudflare_ip = request.headers.get("Cf-Connecting-IP")

        if forwarded_for:
            user_id = forwarded_for.split(",")[0].strip()
        elif cloudflare_ip:
            user_id = cloudflare_ip
        else:
            user_id = request.client.host

    except (AttributeError, RuntimeError, fastapi.exceptions.FastAPIError):
        user_id = "default_user"

    # Rate limiting
    if rate_limiter.is_rate_limited(user_id):
        return (
            "You're sending messages too quickly. "
            "Please wait a moment before sending another message."
        )

    # Track token usage
    prompt_tokens = 0
    completion_tokens = 0
    anthropic_input_tokens = 0
    anthropic_output_tokens = 0

    # Build OpenAI messages
    messages = list(system)

    for item in history:
        if isinstance(item, dict) and "role" in item:
            messages.append(item)

        elif isinstance(item, (list, tuple)) and len(item) == 2:
            user_message, assistant_message = item

            if user_message is not None:
                messages.append({
                    "role": "user",
                    "content": user_message
                })

            if assistant_message is not None:
                messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })

    messages.append({
        "role": "user",
        "content": message
    })

    # First OpenAI response
    response = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools
    )

    if response.usage:
        prompt_tokens += response.usage.prompt_tokens
        completion_tokens += response.usage.completion_tokens

    # Handle tool calls
    while response.choices[0].finish_reason == "tool_calls":
        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls

        results = handle_tool_calls(tool_calls)

        messages.append(assistant_message)
        messages.extend(results)

        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools
        )

        if response.usage:
            prompt_tokens += response.usage.prompt_tokens
            completion_tokens += response.usage.completion_tokens

    reply = response.choices[0].message.content

    # First evaluation
    evaluation = evaluate(
        reply=reply,
        message=message,
        history=history
    )

    anthropic_input_tokens += evaluation.input_tokens
    anthropic_output_tokens += evaluation.output_tokens

    print(
        f"Evaluation: {evaluation.is_acceptable} | "
        f"{evaluation.feedback}",
        flush=True
    )

    regenerated = False

    # Regenerate once if evaluator rejects the response
    if not evaluation.is_acceptable:
        regenerated = True

        messages.append({
            "role": "assistant",
            "content": reply
        })

        messages.append({
            "role": "user",
            "content": (
                "Improve your previous response based on the evaluator "
                "feedback below. Answer the user's original request, "
                "not this instruction.\n\n"
                f"Evaluator feedback: {evaluation.feedback}"
            )
        })

        # Regenerated OpenAI response
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools
        )

        if response.usage:
            prompt_tokens += response.usage.prompt_tokens
            completion_tokens += response.usage.completion_tokens

        # Handle tool calls during regeneration
        while response.choices[0].finish_reason == "tool_calls":
            assistant_message = response.choices[0].message
            tool_calls = assistant_message.tool_calls

            results = handle_tool_calls(tool_calls)

            messages.append(assistant_message)
            messages.extend(results)

            response = openai.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools
            )

            if response.usage:
                prompt_tokens += response.usage.prompt_tokens
                completion_tokens += response.usage.completion_tokens

        reply = response.choices[0].message.content

        # Evaluate regenerated response
        second_evaluation = evaluate(
            reply=reply,
            message=message,
            history=history
        )

        anthropic_input_tokens += second_evaluation.input_tokens
        anthropic_output_tokens += second_evaluation.output_tokens

        evaluation = second_evaluation

        print(
            f"Re-evaluation: {evaluation.is_acceptable} | "
            f"{evaluation.feedback}",
            flush=True
        )

    # Final metrics
    latency_seconds = time.perf_counter() - started_at

    print(
        f"Latency: {latency_seconds:.2f}s | "
        f"OpenAI tokens: {prompt_tokens + completion_tokens} | "
        f"Anthropic tokens: "
        f"{anthropic_input_tokens + anthropic_output_tokens}",
        flush=True
    )

    # Send usage metrics to Telegram
    try:
        record_usage_metrics(
            latency_seconds=latency_seconds,
            openai_prompt_tokens=prompt_tokens,
            openai_completion_tokens=completion_tokens,
            anthropic_input_tokens=anthropic_input_tokens,
            anthropic_output_tokens=anthropic_output_tokens,
            evaluator_accepted=evaluation.is_acceptable,
            regenerated=regenerated
        )

    except Exception as error:
        # Metrics should never break the chat
        print(
            f"Could not send usage metrics to Telegram: {error}",
            flush=True
        )

    return reply

if __name__ == "__main__":
    demo = gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Digital Twin",
        description="Talk to my AI twin about my career",
        chatbot=gr.Chatbot(
            show_label=False,
            elem_classes=["chatbot"],
        ),
        css=CSS,
        js=JS,
        theme=gr.themes.Base(),
    )
    demo.launch()
