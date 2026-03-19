# Experiment Specification

## Topic
Large language models (LLMs) are increasingly deployed as agents that interact with external systems through tools and application programming interfaces (APIs). Modern deployments allow LLMs to execute code, query databases, control software systems, and trigger automated workflows. As a result, these models are no longer limited to generating text responses; they can now perform actions that influence real systems. Ensuring the safe behavior of such agentic LLM systems has therefore become an important challenge for AI deployment.
Most current safety mechanisms for LLMs rely on alignment methods such as reinforcement learning from human feedback (RLHF) and related post-training techniques. These methods train models to refuse harmful instructions or provide safety warnings during conversation. As a result, many aligned models exhibit strong refusal behavior when directly asked to perform unsafe tasks in text-based interactions. However, most safety evaluations measure behavior in conversational settings where the model only produces language outputs.
In practice, many deployed LLM agents are given access to external tools, including command-line interfaces, code execution environments, device APIs, and database operations. This expanded capability changes the safety threat model: rather than merely describing an action in text, the model can perform the action through a tool invocation. This raises an important question for AI safety: do conversational safety behaviors learned during training transfer to environments where models can execute actions?
In this work, we investigate a phenomenon we call the conversation–action gap, where safety behavior observed during conversation does not generalize to tool-enabled environments. When interacting purely through conversation, models often refuse unsafe requests or respond with high-level warnings. However, when given access to tools capable of executing commands, the same models may perform actions related to the request rather than refusing it.
To study this effect, we introduce the Conversation–Action Gap evaluation framework, which compares model behavior under two matched interaction modes: text-only conversation (chat mode) and tool-enabled interaction (tool mode). Using identical prompts across both modes allows us to isolate the effect of tool availability on model behavior.
We conduct a pilot evaluation using three frontier models—Claude Sonnet 4, GPT-4o, and Gemini 2.5 Flash—across prompts drawn from public safety benchmarks and self-generated cyberphysical scenarios. In the pilot results, compliance behavior increases when tools are available: compliance rises from 14.4% in chat mode to 22.2% in tool mode, while refusal decreases from 81.1% to 65.6%.


## Project Structure
Multi-file experiment project with 6 file(s): `baselines.py`, `data_loader.py`, `main.py`, `methods.py`, `metrics.py`, `models.py`

## Entry Point
`main.py` — executed directly via sandbox

## Outputs
- `main.py` emits metric lines in `name: value` format
- Primary metric key: `compliance_rate`

## Topic-Experiment Alignment
ALIGNED

## Constraints
- Time budget per run: 600s
- Max iterations: 10
- Self-contained execution (no external data, no network)
- Validated: Code validation: 6 warning(s)

## Generated
2026-03-17T03:46:08+00:00
