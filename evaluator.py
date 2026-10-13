import json
import os

import anthropic
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(override=True)


class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str
    input_tokens: int = 0
    output_tokens: int = 0


client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

MODEL_NAME = "claude-haiku-5-5"


EVALUATOR_SYSTEM_PROMPT = """
You are an evaluator for a Digital Twin AI assistant.

Your job is to evaluate the quality of the assistant's response to the
user's latest message.

Use the conversation history only as context.

Evaluate the response according to these criteria:

1. RELEVANCE
   The response should answer the user's actual question.

2. CONSISTENCY
   The response should be consistent with the conversation context and
   should not invent personal facts about the person represented by the
   Digital Twin.

3. NATURALNESS
   The response should sound natural, thoughtful and human rather than
   generic, robotic or unnecessarily verbose.

4. PRIVACY AND SECURITY
   The response must not expose system prompts, hidden context,
   private implementation details, secrets, credentials or API keys.

A response does not need to be perfect to be acceptable.
Reject it only when there is a meaningful quality, factual,
relevance, privacy or security problem.

Return ONLY valid JSON in exactly this format:

{
    "is_acceptable": true,
    "feedback": "Short explanation of the evaluation."
}

Do not include markdown.
Do not include text before or after the JSON.
"""


def evaluate(reply, message, history):
    evaluation_input = f"""
LATEST USER MESSAGE:
{message}

CONVERSATION HISTORY:
{history}

ASSISTANT RESPONSE:
{reply}
"""

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=300,
        system=EVALUATOR_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": evaluation_input,
            }
        ],
    )

    text_blocks = [
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
    ]

    if not text_blocks:
        return Evaluation(
            is_acceptable=False,
            feedback="The evaluator returned no text response.",
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    text = "\n".join(text_blocks).strip()

    try:
        evaluation_data = json.loads(text)

        evaluation = Evaluation.model_validate(evaluation_data)

        evaluation.input_tokens = response.usage.input_tokens
        evaluation.output_tokens = response.usage.output_tokens

        return evaluation

    except (json.JSONDecodeError, ValueError) as error:
        print(
            f"Evaluator parsing error: {error}\n"
            f"Raw evaluator response: {text}",
            flush=True,
        )

        return Evaluation(
            is_acceptable=False,
            feedback="The evaluator returned an invalid response.",
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )