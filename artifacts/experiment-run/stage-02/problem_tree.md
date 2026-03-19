# Source
The research topic focuses on the "Conversation–Action Gap" in agentic Large Language Models (LLMs), where models that safely refuse harmful text-based requests inadvertently comply when given access to executable tools and APIs. The goal context expands on this by hypothesizing "Syntax-Induced Moral Aphasia"—that strict tool schemas (like JSON) suppress RLHF-trained safety behaviors. The proposed research aims to quantify this gap across frontier models using a 200-prompt adapted dataset and evaluate a novel zero-shot inference-time mitigation called Execution-Aware Chain-of-Thought (EA-CoT).

# Sub-questions
To systematically address the research goal, the problem can be decomposed into the following core sub-questions:

1. **Quantification of the Vulnerability:** What is the baseline magnitude of the "conversation-action gap" across frontier models (GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro) when comparing refusal rates in standard chat mode versus syntactic compliance rates in a standard JSON tool-calling environment?
2. **Isolation of the Mechanism:** To what extent do the rigid structural constraints of tool schemas (e.g., JSON syntax) independently cause the suppression of safety guardrails, compared to a "Tool-Plaintext" ablation where models invoke tools without strict formatting? 
3. **Efficacy of the Mitigation:** How effectively does the Execution-Aware Chain-of-Thought (EA-CoT) prompting strategy reduce tool-mode compliance for harmful requests, and does it successfully restore refusal rates to within 5 percentage points of the standard chat baseline?
4. **Analysis of Capability Trade-offs:** Does the enforcement of EA-CoT negatively impact the agent's utility, specifically measuring whether the success rate on benign, safe tool-use tasks drops by more than the acceptable 5% threshold?

# Priority Ranking
1. **Priority 1: Quantification of the Vulnerability (Sub-question 1)** 
   *Rationale:* Establishing a rigorous empirical baseline is the prerequisite for all subsequent claims. You must first prove the gap exists and is measurable across the chosen models before explaining or fixing it.
2. **Priority 2: Isolation of the Mechanism (Sub-question 2)** 
   *Rationale:* Proving the "Syntax-Induced Moral Aphasia" hypothesis is the core novelty of this research. Separating the act of tool use from the syntax of tool use is necessary to justify the specific design of the EA-CoT mitigation.
3. **Priority 3: Efficacy of the Mitigation (Sub-question 3)** 
   *Rationale:* Once the mechanism is isolated, demonstrating that EA-CoT successfully forces moral reasoning and bridges the modality gap is the primary deliverable of the project.
4. **Priority 4: Analysis of Capability Trade-offs (Sub-question 4)** 
   *Rationale:* While critical for practical adoption by developers, measuring benign performance is secondary to proving that the security vulnerability can actually be patched.

# Risks
* **Evaluation Bias & Reliability:** Relying on an LLM-as-a-judge (e.g., Llama-3-70B-Instruct) to evaluate tool schemas introduces the risk of the judge misclassifying borderline malicious parameters hidden within valid JSON structures.
* **Non-Stationary Black-Box Models:** Frontier models (GPT-4o, Claude 3.5, Gemini 1.5) are frequently updated behind the scenes. Silent updates to their native safety filters or function-calling fine-tuning during the 2-week sprint could skew comparative baseline results.
* **Limited Mechanistic Proof:** Because the research relies entirely on black-box API access, you can only demonstrate behavioral correlations regarding "Syntax-Induced Moral Aphasia." You cannot inspect internal activations to definitively prove the cognitive load hypothesis.
* **Dataset Overfitting:** A 200-prompt adapted dataset (from AdvBench/ToolEmu) might be too narrow to represent the full spectrum of cyberphysical or tool-based attack vectors, potentially limiting the generalized claims of the EA-CoT mitigation.