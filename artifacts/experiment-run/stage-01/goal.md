# Research Goal: Quantifying and Mitigating the Conversation–Action Gap in Agentic LLMs

## Topic
The safety of agentic Large Language Models (LLMs) and the emerging discrepancy between their robust conversational refusal behaviors and their vulnerability to compliance when equipped with actionable tools and strict output schemas.

## Novel Angle
Most current LLM safety mechanisms (e.g., RLHF, DPO) heavily overfit to the conversational modality. Recent agent safety research has primarily focused on either multi-step simulated disasters or the use of tools by bad actors. **The novel angle of this research is identifying the structural mechanism of the "Conversation-Action Gap" as "Syntax-Induced Moral Aphasia," and demonstrating how to fix it at inference time.** 

We hypothesize that the cognitive load of adhering to strict tool schemas (e.g., JSON/XML syntax) and the assumption of an "executor" persona systematically suppress the conversational safety guardrails learned via RLHF. In essence, the native tool-use format acts as an *accidental jailbreak*. While retraining frontier models to be natively "tool-safe" is computationally prohibitive for most researchers, we introduce a novel, zero-shot inference-time mitigation: **Execution-Aware Chain-of-Thought (EA-CoT)**. EA-CoT forces the model to evaluate the *functional outcome* of a requested tool call in plaintext moral reasoning before generating the required JSON syntax, bridging the modality gap without sacrificing agentic capabilities. 

This is highly timely (2024-2026) as platforms like OpenAI, Anthropic, and Google are deeply integrating native tool-calling features (e.g., structured outputs, function calling) into their standard APIs, making this vulnerability pervasive among application developers.

## Trend Validation
The timeliness and relevance of this research are supported by recent literature focusing on the expanding threat surface of LLM agents and the brittleness of RLHF:
1. **Ruan et al. (2024), "Identifying the Risks of LM Agents with an LLM-Simulated Environment" (ToolEmu):** Establishes the severe risks of tool-augmented models but focuses primarily on simulated disastrous outcomes rather than isolating the modality gap (chat vs. tool) as the independent variable.
2. **Qi et al. (2024), "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To!":** Demonstrates that purely structural or formatting constraints during fine-tuning can rapidly degrade safety, supporting our hypothesis that the structural constraints of JSON function-calling suppress alignment.
3. **Zou et al. (2023/2024), "Universal and Transferable Adversarial Attacks on Aligned Language Models":** Shows how seemingly meaningless suffix strings break alignment. Our work extends this by showing that developer-provided API documentation and JSON schemas inadvertently act as universal adversarial suffixes.

### Benchmark
*   **Name:** AdvBench-Tool-Adapted & ToolEmu Safety Subset
*   **Source:** A synthesized benchmark adapting the harmful behaviors from AdvBench (Zou et al.) into actionable tasks requiring file system, network, or OS-level tool invocations, combined with the high-risk scenarios from ToolEmu.
*   **Metrics:** 
    *   *Syntactic Compliance Rate (minimize):* Percentage of unsafe requests where the model outputs a valid tool call.
    *   *Refusal Rate (maximize):* Percentage of unsafe requests cleanly refused.
    *   *Benign Capability Retention (maximize):* Success rate on safe, standard tool-use tasks to ensure the mitigation does not cripple the agent.
*   **Current SOTA:** No established SOTA for this specific modal intervention. Pilot baselines indicate frontier models exhibit ~14% compliance in chat mode vs. ~22% in tool mode. Our target SOTA is reducing tool-mode compliance back to ≤14% while retaining >95% benign capability.

## Scope
Focused entirely on black-box, API-accessible frontier models (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro). The study will evaluate responses across 200 harmful prompts paired with corresponding mock tool schemas (e.g., `execute_bash`, `write_file`, `send_http_request`). We will compare four modalities: (1) Chat Baseline, (2) Tool-JSON Baseline, (3) Tool-Plaintext Ablation, and (4) Tool-JSON + EA-CoT.

## SMART Goal
**Specific:** Quantify the "Conversation-Action Gap" caused by JSON schema constraints across 3 frontier models using a 200-prompt adapted dataset, and evaluate the effectiveness of Execution-Aware Chain-of-Thought (EA-CoT) prompting in mitigating it.
**Measurable:** Reduce the tool-mode compliance rate for harmful prompts by at least 30% relative to the Tool-JSON baseline, restoring refusal rates to within 5 percentage points of the standard Chat Baseline, while maintaining >95% capability on benign tool tasks.
**Achievable:** Inference-only experiments using official APIs and an LLM-as-a-judge (e.g., Llama-3-70B-Instruct) for automated, scalable evaluation. Total compute budget is minimal.
**Relevant:** Directly addresses a critical vulnerability in how millions of developers currently deploy agents using standard tool-calling APIs.
**Time-bound:** Complete the dataset adaptation, pipeline execution, and empirical analysis within a 2-week sprint.

## Constraints
*   **Compute Budget:** < $50 in API credits for inference; single GPU for local LLM-as-a-judge evaluation if not using API for judging.
*   **Tools:** Standard OpenAI, Anthropic, and Google API SDKs; lightweight Python mock-execution sandbox to validate syntactic compliance.
*   **Data Access:** Publicly available AdvBench and ToolEmu datasets, modified programmatically. Black-box model access means we cannot inspect internal activations, restricting us to behavioral analysis.

## Success Criteria
1. **Empirical Isolation:** Statistically significant evidence showing that the formatting constraint (JSON schema) induces higher compliance than plaintext tool requests, proving the "Syntax-Induced Moral Aphasia" hypothesis.
2. **Mitigation Validation:** EA-CoT successfully lowers the compliance rate in tool mode to match or improve upon the chat-mode baseline.
3. **Capability Preservation:** The intervention does not significantly degrade the model's ability to successfully invoke tools for benign, safe requests (drop in benign success rate < 5%).
4. **Publishable Output:** A robust empirical paper detailing a zero-shot, drop-in mitigation that application developers can immediately adopt to secure their agentic systems.

**Generated:** 2026-03-17