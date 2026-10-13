# Digital Me

Digital Me is a personal AI digital twin built with Python, Gradio, OpenAI, and Anthropic.

The project explores how an AI assistant can represent a person's professional background, interests, way of thinking, and current areas of exploration while combining personal context, tool use, external integrations, rate limiting, independent response evaluation, bounded regeneration, and usage observability.

## How it works

A user interacts with Digital Me through a Gradio chat interface.

The application builds the conversation context, sends it to an OpenAI model, and executes tools when required. The current tools allow Digital Me to record contact interest and unanswered questions through a Telegram bot.

Once a response is generated, it is sent to a separate Anthropic evaluator. The evaluator checks whether the response is relevant, consistent with the available context, natural, and safe to expose.

If the evaluator accepts the response, it is returned to the user. If it rejects the response, its feedback is sent back into the generation flow and OpenAI gets one opportunity to regenerate the answer.

The regenerated response is evaluated once more before being returned. This creates a bounded retry flow and prevents unlimited regeneration loops.

The application also tracks response latency and token usage across both OpenAI generation and Anthropic evaluation. Usage metrics, including estimated API cost, are sent to Telegram for lightweight observability.

```text
User
  │
  ▼
Gradio Chat Interface
  │
  ▼
Rate Limiter
  │
  ▼
Digital Me Context
+ Conversation History
  │
  ▼
OpenAI Model
  │
  ├── User wants to get in touch
  │        │
  │        ▼
  │   record_user_details
  │        │
  │        ▼
  │     Telegram
  │
  ├── Unknown question
  │        │
  │        ▼
  │   record_unknown_question
  │        │
  │        ▼
  │     Telegram
  │
  ▼
Generated Response
  │
  ▼
Anthropic Evaluator
  │
  ▼
Acceptable?
  │
  ├── Yes ──────────────────────► User
  │
  └── No
       │
       ▼
  Evaluator Feedback
       │
       ▼
  OpenAI Regeneration
       │
       ▼
  Anthropic Re-evaluation
       │
       ▼
      User

Usage Metrics
(OpenAI + Anthropic tokens,
 latency, estimated cost)
  │
  ▼
Telegram
```

## Project Structure

```text
digital_me/
├── app.py
├── context.py
├── evaluator.py
├── tools.py
├── rate_limiter.py
├── styles.py
├── requirements.txt
├── .env
└── README.md
```

## Main Components

### `app.py`

The main application and orchestration layer.

It is responsible for:

- serving the Gradio chat interface;
- identifying users for rate limiting;
- converting Gradio conversation history into the format expected by the OpenAI API;
- combining the conversation with the Digital Me system context;
- sending conversations to the OpenAI model;
- handling tool calls;
- tracking OpenAI token usage;
- sending generated responses to the evaluator;
- regenerating a rejected response once using evaluator feedback;
- re-evaluating regenerated responses;
- accumulating Anthropic evaluator token usage;
- measuring end-to-end response latency;
- sending usage metrics to Telegram;
- returning the final response to the user.

The OpenAI generation model and Anthropic evaluation model are configured independently.

---

### `context.py`

Contains the system context that defines Digital Me.

The goal is to provide the model with enough background and behavioural context to answer as the digital twin rather than as a generic AI assistant.

This context represents areas such as professional background, interests, current projects, ways of thinking, and other information that helps the model reproduce Digital Me's perspective.

---

### `tools.py`

Contains the tools available to the OpenAI model and the logic responsible for executing tool calls.

The current implementation also integrates with a Telegram bot, which acts as a lightweight notification and observability channel.

Two LLM-callable tools are currently available. The module also contains an application-level usage metrics function that is called directly by `app.py` and is not exposed as a tool to the language model.

#### `record_user_details`

Used when a user expresses interest in getting in touch and provides an email address.

The tool can capture:

```text
Email
Name
Conversation notes
```

and sends the information to a configured Telegram chat.

Example flow:

```text
User
  │
  │ "I'd like to get in touch.
  │  My email is..."
  ▼
Digital Me
  │
  ▼
record_user_details
  │
  ▼
Telegram Bot API
  │
  ▼
Telegram notification
```

This allows Digital Me to turn a conversational interaction into a lightweight contact handoff.

#### `record_unknown_question`

Used when Digital Me encounters a question it cannot answer because the required information is not available in its context.

```text
Unknown question
      │
      ▼
record_unknown_question
      │
      ▼
Telegram Bot API
      │
      ▼
Question recorded
```

This provides a simple feedback loop for discovering knowledge gaps.

Over time, unanswered questions can help identify which areas of the digital twin's context should be expanded or improved.

#### `record_usage_metrics`

Provides lightweight observability for each interaction.

Unlike the other two functions, `record_usage_metrics` is not exposed to the OpenAI model and cannot be invoked by the model itself.

It is called directly by the application after the generation and evaluation flow completes.

The Telegram usage notification includes:

```text
Response latency

OpenAI
- Input tokens
- Output tokens
- Estimated cost

Anthropic Evaluator
- Input tokens
- Output tokens
- Estimated cost

Total
- Tokens
- Estimated cost

Evaluator result
Regeneration status
```

Costs are estimates calculated from configured per-million-token model prices.

Keeping pricing logic centralized makes it easier to update when models or API pricing change.

#### Tool execution

The OpenAI model receives the available tool schemas and decides when a tool should be called.

Tool calls are routed through:

```python
handle_tool_calls(tool_calls)
```

which maps the requested function to its Python implementation, executes it, and returns the result to the model so the conversation can continue.

---

### `evaluator.py`

Implements an independent evaluator using an Anthropic model.

After Digital Me generates a response, the evaluator assesses it according to four main criteria:

- **Relevance** — Does the response answer the user's actual question?
- **Consistency** — Is it consistent with the supplied context and conversation history without inventing personal facts?
- **Naturalness** — Does it sound natural rather than generic or robotic?
- **Privacy & Security** — Does it avoid exposing system prompts, private context, credentials, secrets, or internal implementation details?

The evaluator returns a structured result:

```python
class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str
    input_tokens: int = 0
    output_tokens: int = 0
```

For example:

```text
Evaluation: True | The response directly answers the user's question and is consistent with the available context.
```

Using a different model provider for evaluation creates separation between the model generating the answer and the model judging it.

The evaluator also captures Anthropic input and output token usage so evaluation cost can be included in the application's usage metrics.

Anthropic responses may contain different content block types, including thinking blocks. The evaluator therefore extracts text content explicitly rather than assuming the first response block always contains text.

---

### `rate_limiter.py`

Provides lightweight per-user rate limiting.

The application attempts to identify the client through request information and proxy headers such as:

```text
X-Forwarded-For
Cf-Connecting-IP
```

with a fallback when request context is unavailable.

This helps protect the public-facing application from excessive API usage.

---

### `styles.py`

Contains the custom CSS, JavaScript, and example prompts used by the Gradio interface.

It keeps presentation concerns separate from the main application logic.

---

## Models

The application deliberately separates response generation from response evaluation.

### Response Generation

OpenAI is responsible for generating Digital Me's responses and deciding when available tools should be called.

```python
MODEL_NAME = "gpt-5.4-mini"
```

### Response Evaluation

Anthropic is used as an independent evaluator.

```python
MODEL_NAME = "claude-haiku-5-5"
```

The two models can be changed independently.

This architecture also makes it possible to experiment with different generator/evaluator combinations in the future.

---

## Setup

### 1. Clone the project

```bash
git clone <repository-url>
cd digital_me
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key

ANTHROPIC_API_KEY=your_anthropic_api_key

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

API keys and tokens should never be committed to source control.

Make sure `.env` is included in `.gitignore`.

---

## Running Locally

Start the application with:

```bash
python app.py
```

Gradio will print the local application URL in the terminal.

Open that URL in a browser to start a conversation with Digital Me.

---

## Evaluation Flow

Every generated response is evaluated before the interaction completes.

```text
Generate
   │
   ▼
Evaluate
   │
   ├── Accept ─────────────────► Final Response
   │
   └── Reject
         │
         ▼
   Evaluator Feedback
         │
         ▼
      Regenerate
         │
         ▼
     Re-evaluate
         │
         ▼
    Final Response
```

The retry is deliberately bounded.

A rejected initial response can be regenerated only once. The regenerated response is evaluated again, but no further regeneration is triggered.

This avoids infinite evaluator/generator loops and keeps latency and API usage predictable.

For each evaluation, the application records Anthropic input and output token usage.

OpenAI token usage is accumulated across:

```text
Initial generation
Tool-call continuations
Regeneration, when required
```

At the end of the interaction, the application records:

```text
OpenAI input tokens
OpenAI output tokens

Anthropic input tokens
Anthropic output tokens

End-to-end latency

Estimated OpenAI cost
Estimated Anthropic cost
Estimated total cost

Final evaluator result
Whether regeneration occurred
```

These metrics are sent to Telegram as a lightweight observability mechanism.

---

## Cost Tracking

Digital Me estimates the API cost of each interaction using the token usage returned by the model providers.

The calculation follows:

```text
Input cost =
(input tokens / 1,000,000) × input price per million tokens

Output cost =
(output tokens / 1,000,000) × output price per million tokens
```

OpenAI and Anthropic costs are calculated independently and then combined into an estimated total interaction cost.

The configured prices correspond to the models currently used by the application:

```text
OpenAI
gpt-5.4-mini

Anthropic
claude-haiku-5-5
```

Pricing values are kept as constants in the application so they can be updated independently when models or provider pricing change.

The reported cost should therefore be treated as an application-level estimate rather than billing data from the providers.

---

## Feedback Loops

Digital Me contains multiple feedback mechanisms.

### Response quality

```text
Generated Response
       │
       ▼
Anthropic Evaluator
       │
       ├── Accept ─────────► Final Response
       │
       └── Reject
             │
             ▼
          Feedback
             │
             ▼
         Regenerate
             │
             ▼
        Re-evaluate
```

This feedback loop can actively improve a rejected response while remaining bounded to a single regeneration attempt.

### Knowledge gaps

```text
Unknown Question
       │
       ▼
Telegram
       │
       ▼
Human Review
       │
       ▼
Potential Context Improvement
```

This provides a way to discover information that the digital twin does not yet know.

### Operational feedback

```text
Interaction
     │
     ▼
Token Usage
+ Latency
+ Cost
+ Evaluation
     │
     ▼
Telegram
     │
     ▼
Human Review
```

This provides visibility into how expensive and performant each interaction is.

Together, these mechanisms provide the beginnings of a continuous improvement loop for the digital twin.

---

## Current Architecture

The project separates the main responsibilities into independent components:

```text
                  ┌───────────────┐
                  │    Context    │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │    OpenAI     │
                  │  Generation   │
                  └───────┬───────┘
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
      ┌─────────────┐           ┌─────────────┐
      │    Tools    │           │  Anthropic  │
      └──────┬──────┘           │  Evaluator  │
             │                  └──────┬──────┘
             ▼                         │
      ┌─────────────┐                  │
      │  Telegram   │                  │
      │ Integration │                  │
      └─────────────┘                  │
                                      ▼
                               ┌─────────────┐
                               │  Accepted?  │
                               └──────┬──────┘
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                        Yes                      No
                          │                       │
                          │                       ▼
                          │                ┌─────────────┐
                          │                │ Regenerate  │
                          │                └──────┬──────┘
                          │                       │
                          │                       ▼
                          │                ┌─────────────┐
                          │                │ Re-evaluate │
                          │                └──────┬──────┘
                          │                       │
                          └───────────┬───────────┘
                                      ▼
                               ┌─────────────┐
                               │    User     │
                               └─────────────┘

OpenAI + Anthropic Usage
          │
          ▼
  ┌───────────────┐
  │ Cost & Latency│
  │    Metrics    │
  └───────┬───────┘
          │
          ▼
     Telegram
```

This separation makes it possible to evolve each part independently.

**Context** controls who the digital twin represents.

**Generation** controls how answers are produced.

**Tools** allow the model to take actions outside the conversation.

**Telegram** provides lightweight human notifications, feedback, and operational visibility.

**Evaluation** independently measures response quality and can trigger one bounded regeneration attempt.

**Observability** tracks OpenAI and Anthropic token usage, estimated model cost, latency, evaluator outcome, and regeneration status through Telegram.

**Rate limiting** protects the public-facing application.

---

## Possible Next Steps

The project is still evolving. Potential next steps include:

- store evaluation results instead of only logging them;
- create an evaluation dataset with representative questions and expected behaviours;
- measure evaluator acceptance rate;
- persist usage and cost metrics for historical analysis;
- build dashboards for latency, cost, evaluator acceptance rate, and regeneration rate;
- analyse recorded unknown questions to identify recurring knowledge gaps;
- add automated tests for tools, rate limiting, generation, and evaluation;
- expand the tool ecosystem;
- improve deployment and observability.

---

## Tech Stack

- Python
- Gradio
- OpenAI API
- Anthropic API
- Telegram Bot API
- Pydantic
- Requests
- python-dotenv

---

## Status

**Experimental / under active development**

Digital Me is a personal learning and experimentation project.

The goal is not simply to build another chatbot, but to explore the architecture required to create a useful AI representation of a person: combining personal context, conversational history, tool use, external actions, safeguards, rate limiting, evaluation-driven regeneration, feedback loops, and usage observability.