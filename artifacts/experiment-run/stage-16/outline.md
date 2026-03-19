Here is the detailed paper outline based on your results and the top-tier academic writing standards.

### Candidate Titles

1. **CAGE: Evaluating the Conversation-Action Gap in Agentic LLMs**
   * **Memorability:** 5/5 (Short, punchy, and uses a highly relevant metaphor)
   * **Specificity:** 4/5 (Clearly states the phenomenon being evaluated)
   * **Novelty Signal:** 4/5 (Introduces a new formalized gap in the literature)
   * **Word Count:** 8 words

2. **CAGE: Uncovering Safety Vulnerabilities in Tool-Enabled Language Models**
   * **Memorability:** 4/5 (Strong acronym, slightly more standard subtitle)
   * **Specificity:** 5/5 (Explicitly links the tool-use aspect to safety vulnerabilities)
   * **Novelty Signal:** 4/5 (Signals a discovery-focused empirical paper)
   * **Word Count:** 9 words

3. **CAGE: Bridging the Conversation-Action Gap for Safe AI Agents**
   * **Memorability:** 4/5 (Action-oriented and positive framing)
   * **Specificity:** 4/5 (Focuses on the mitigation and agentic context)
   * **Novelty Signal:** 5/5 (Implies both the discovery of a gap and its resolution)
   * **Word Count:** 9 words

***

### Paper Outline

#### Abstract
**Word Count Target:** 180-220 words
**Section Goal:** Follow the strict PMR+ (Problem, Method, Results) structure to hook the reader. The first two sentences will critique the status quo of relying on text-based alignment (RLHF) for agentic models, stating the gap that conversational safety does not transfer to tool-enabled environments. The next two sentences will introduce the Conversation-Action Gap Evaluation (CAGE) framework and our key insight that tool availability fundamentally alters the threat model. The final sentences will report concrete quantitative claims, specifically contrasting the standard chat baseline with the standard tool baseline, and highlighting the performance of our Execution-Aware Chain-of-Thought (EA-CoT) mitigation.
**Evidence Links:** 
* Cite the baseline shift (StandardChatBaseline at 0.0% vs. StandardToolBaseline at 31.67% compliance).
* Cite the mitigation success (ExecutionAwareCoTMethod reducing compliance to 0.0% while maintaining a 96.67% success rate).

#### 1. Introduction
**Word Count Target:** 800-1000 words
**Section Goal:** Establish the motivation, gap, approach, and contributions across four distinct paragraphs. The opening paragraph will motivate the increasing deployment of LLMs as agents with API and tool access. The second paragraph will identify the critical gap: current alignment methods measure conversational refusal, but deployed agents can execute actions, leading to the "conversation-action gap." The third paragraph will detail our approach, introducing the CAGE framework to isolate the effect of tool availability using matched interaction modes. The final paragraph will provide a concrete list of three to four specific contributions, including the empirical validation of the gap and the introduction of mitigation strategies.
**Evidence Links:**
* Reference the pilot findings (compliance rising from 14.4% in chat mode to 22.2% in tool mode).
* Introduce the refined experimental results demonstrating a 31.67% compliance rate when tools are explicitly available.

#### 2. Related Work
**Word Count Target:** 600-800 words
**Section Goal:** Organize the literature into cohesive sub-topics rather than a flat list, targeting at least 15 unique references. The first subsection will cover "LLM Safety and Alignment," focusing on RLHF and text-based refusal training. The second subsection will explore "Agentic LLMs and Tool Use," discussing how code execution and API access have expanded model capabilities. The final subsection will address "Evaluation Frameworks for AI Safety," specifically looking at red-teaming and benchmark design. Each subsection will conclude with a clear transition explaining how CAGE differs by explicitly contrasting matched chat and tool modes.
**Evidence Links:** 
* Connect the limitations of purely conversational safety benchmarks to the necessity of the CAGE methodology.

#### 3. Method: The CAGE Framework
**Word Count Target:** 1000-1500 words
**Section Goal:** Provide a rigorous technical description of the evaluation framework and mitigation strategies written as a flowing narrative. This section will start with the problem formulation, defining the objective function for measuring compliance and success rates mathematically. We will detail the exact mechanics of the matched interaction modes—Standard Chat Baseline versus Standard Tool Baseline. Finally, we will introduce the Execution-Aware CoT (EA-CoT) and the Production Stakes Prompt Method, using an algorithm environment to present the pseudocode for how tool-invocation intent is parsed and evaluated before execution.
**Evidence Links:**
* Formalize the metrics used in the results table: `compliance_rate` and `success_rate`.
* Define the architectural differences between the `ExecutionAwareCoTMethod` and the `CoTWithoutExecutionFocusAblation`.

#### 4. Experimental Setup
**Word Count Target:** 800-1200 words
**Section Goal:** Detail the experimental design necessary to reproduce the findings, acknowledging the rigorous scaling required to achieve statistical power. This section will describe the dataset composition, consisting of strictly partitioned safety prompts and benign prompts to measure both compliance and success rates. We will specify the three frontier models tested (Claude Sonnet 4, GPT-4o, and Gemini 2.5 Flash) and detail the exact system prompts and hardware configurations. A mandatory hyperparameter table (Table 1) will be included. We will emphasize the rigorous validation checks implemented to ensure tool modes actively provide functional tools, addressing prior ablation implementation failures.
**Evidence Links:**
* Reference the necessity of N $\ge$ 400 prompts per condition (derived from the power analysis) to reliably detect the ~5% effect sizes.
* Detail the 7 specific experimental conditions (e.g., PollutedChatBaseline, ExplicitRejectionToolMethod).

#### 5. Results and Analysis
**Word Count Target:** 600-800 words
**Section Goal:** Present the quantitative outcomes of the experiments through descriptive text and centralized tables, without repeating the numbers verbatim in the prose. We will provide a main results table detailing the performance across all baselines and mitigation methods. The analytical paragraphs will dissect the severity of the conversation-action gap, contrasting the 0.0% compliance of the chat baseline against the 31.67% compliance of the tool baseline. We will then analyze the ablation study, demonstrating that while the CoT Without Execution Focus ablation still allowed a 6.67% compliance rate, the full Execution-Aware CoT method successfully reduced unsafe compliance to 0.0% with minimal degradation to benign success rates (96.67%).
**Evidence Links:**
* The comprehensive LaTeX table containing the refined iteration metrics.
* Visual references to figures (e.g., "As shown in Figure 1, the compliance rate spikes when tools are introduced...").

#### 6. Discussion
**Word Count Target:** 400-600 words
**Section Goal:** Contextualize the quantitative results within the broader landscape of AI safety. We will discuss why aligned models drop their refusal behaviors when presented with executable formats, hypothesizing that training distributions heavily bias refusals toward conversational text patterns rather than structured API calls. We will evaluate the effectiveness and practical deployment trade-offs of the proposed mitigations, specifically noting why Execution-Aware CoT succeeds where simpler explicit rejection tools fail.
**Evidence Links:**
* Cite prior alignment literature to explain the model-specific effects (e.g., Claude Sonnet-4's baseline resistance versus other models).
* Link the 96.67% success rate of EA-CoT to deployment viability discussions.

#### 7. Limitations
**Word Count Target:** 200-300 words
**Section Goal:** Transparently address the concrete methodological boundaries of the study in a dedicated section. We will discuss the reliance on binary compliance coding, which may obscure the nuance of partially harmful actions. We will also address the challenges of generalizability, noting that while the sample size was scaled for statistical power, the specific tool schemas evaluated may not represent the full diversity of production software environments. Furthermore, we will explicitly acknowledge the potential for model-specific effects dictating the baseline vulnerabilities.
**Evidence Links:**
* Reference the metric validity concerns and the temporal stability of safety behaviors as models undergo continuous updates.

#### 8. Conclusion
**Word Count Target:** 100-200 words
**Section Goal:** Deliver a concise, powerful synthesis of the paper's core thesis and findings. In two to three sentences, we will summarize that the CAGE framework successfully isolates and proves the conversation-action gap, demonstrating that current alignment techniques are insufficient for agentic deployments. The final sentences will propose future work, suggesting the integration of execution-aware safety mechanisms directly into the post-training pipeline of next-generation LLM agents.
**Evidence Links:**
* Final recall of the shift from chat-based safety to action-based vulnerability.