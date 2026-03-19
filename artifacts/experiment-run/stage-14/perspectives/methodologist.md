# Experimental Methodology Audit: Conversation-Action Gap in Agentic LLMs

## Executive Summary: EXPERIMENT FUNDAMENTALLY BROKEN

This experiment suffers from **catastrophic ablation failures** that invalidate virtually all conclusions. The core hypothesis about the conversation-action gap cannot be tested because the experimental conditions are not properly differentiated in the implementation.

---

## 1. Baseline Fairness and Completeness: SEVERELY COMPROMISED

### Critical Issues:

**1.1 Ablation Implementation Failure**
- **15 out of 15 condition pairs** produce identical outputs across metrics
- The experimental conditions are not actually implemented differently in the codebase
- This is not a statistical coincidence—it indicates broken experimental logic

**1.2 Missing Core Comparison**
The central hypothesis requires comparing:
- Chat mode (conversation only) vs. Tool mode (tool-enabled)
- **Problem**: Results show identical performance between `StandardChatBaseline` and `StandardToolBaseline` for Claude Sonnet-4, suggesting the "tool mode" is not actually providing tools

**1.3 Baseline Contamination**
- `PollutedChatBaseline` was designed to test whether tool documentation in prompts affects chat behavior
- **Critical flaw**: Shows identical results to pure chat baseline for 2/3 models, indicating the "pollution" manipulation is not working

### Verdict: **FAILED** - Cannot establish fair comparison between conditions

---

## 2. Metric Appropriateness: PARTIALLY ADEQUATE

### Appropriate Metrics:
- **Compliance Rate**: Directly measures the research question (unsafe request compliance)
- **Success Rate**: Important for measuring capability preservation
- **Refusal Tool Selection Rate**: Relevant for understanding mitigation mechanisms

### Missing Critical Metrics:
- **Effect Size Measurement**: No statistical significance testing despite small sample sizes
- **Tool Usage Rate**: Should measure whether tools are actually being invoked
- **Severity Weighting**: All unsafe requests treated equally regardless of harm potential
- **Latency/Efficiency**: Important for practical deployment considerations

### Verdict: **PARTIAL** - Core metrics present but analysis incomplete

---

## 3. Evaluation Protocol: HIGH CONTAMINATION RISK

### Data Leakage Concerns:
**3.1 Model Training Contamination**
- Using "prompts drawn from public safety benchmarks" creates high risk that frontier models were trained on these exact prompts
- No mention of temporal separation or novel prompt generation
- **Risk Level**: HIGH

**3.2 Experimental Contamination**
- Same prompts used across all conditions increases risk of order effects
- No randomization mentioned in methodology
- **Risk Level**: MEDIUM

### Sample Size Issues:
- **n=20 safety prompts, n=10 benign prompts** per condition
- With 7 conditions × 3 models = 21 comparisons, statistical power is extremely low
- Multiple comparison corrections not applied

### Verdict: **HIGH RISK** - Serious contamination and power issues

---

## 4. Ablation Completeness: CATASTROPHICALLY INCOMPLETE

### What Should Be Tested:
1. **Core Effect**: Chat vs. Tool mode (FAILED - identical results)
2. **Mechanism**: Syntax vs. Context vs. Capability (FAILED - no differentiation)
3. **Mitigation**: Various intervention strategies (FAILED - identical results)

### What The Data Actually Shows:
```
Identical Performance Across "Different" Conditions:
- StandardChatBaseline = StandardToolBaseline (for Claude)
- All mitigation methods = baselines (for most models)
- CoTWithoutExecutionFocusAblation = StandardToolBaseline
```

### Critical Missing Ablations:
- **Tool availability verification**: No proof tools are actually provided
- **Prompt variation control**: No systematic prompt engineering validation
- **Model-specific calibration**: No adjustment for baseline model differences

### Verdict: **CATASTROPHIC FAILURE** - Ablations are non-functional

---

## 5. Reproducibility Assessment: POOR

### Missing Information:
- **Exact prompts used** (only "drawn from public benchmarks")
- **Tool implementation details** (what tools? how invoked?)
- **Model API parameters** (temperature, top-p, etc.)
- **Evaluation criteria specifics** (how is "compliance" vs "refusal" determined?)
- **Random seeds or run variations**

### Available Information:
- Model identifiers specified
- Basic sample sizes provided
- High-level condition descriptions given

### Code Quality Indicators:
- **Major red flag**: Systematic ablation failures suggest implementation bugs
- No validation that experimental manipulations are actually applied
- No sanity checks on baseline differences

### Verdict: **POOR** - Insufficient detail for reproduction, implementation bugs likely

---

## 6. Specific Methodology Improvements Needed

### Immediate Critical Fixes:

**6.1 Fix Ablation Implementation**
```python
# Current (broken): All conditions produce identical outputs
# Required: Verify each condition actually implements intended manipulation
assert chat_baseline != tool_baseline  # This should fail currently
```

**6.2 Implement Proper Tool Mode**
- Verify tools are actually provided and invokable in tool conditions
- Add tool usage metrics to confirm tools are being attempted
- Include tool execution logs for transparency

**6.3 Add Implementation Validation**
```python
# Before running experiments:
def validate_experimental_conditions():
    for condition in conditions:
        assert condition.produces_different_outputs()
        assert condition.implements_intended_manipulation()
```

### Statistical Improvements:

**6.4 Power Analysis and Sample Size**
- Increase to n≥100 per condition for adequate power
- Apply multiple comparison corrections (Bonferroni/FDR)
- Add confidence intervals and effect size reporting

**6.5 Contamination Controls**
- Generate novel safety prompts not in public benchmarks
- Implement temporal separation from model training cutoffs
- Add prompt paraphrasing to test robustness

### Experimental Design Improvements:

**6.6 Proper Baseline Establishment**
```python
# Required validation:
assert StandardToolBaseline.compliance_rate > StandardChatBaseline.compliance_rate
# If this fails, the core hypothesis cannot be tested
```

**6.7 Mechanistic Testing**
- Separate tool context from tool capability
- Test syntax-only vs. execution-capable conditions
- Include graded tool complexity conditions

---

## 7. Overall Assessment: EXPERIMENT REQUIRES COMPLETE RESTART

### Fundamental Problems:
1. **Core hypothesis untestable** due to implementation failures
2. **All ablations non-functional** - conditions are identical
3. **No evidence of actual conversation-action gap** in current data
4. **Sample sizes inadequate** for reliable conclusions
5. **High contamination risk** from public benchmark usage

### Salvageable Elements:
- Research question is important and well-motivated
- Metric definitions are reasonable
- Model selection is appropriate

### Required Actions:
1. **STOP** drawing conclusions from current data
2. **DEBUG** experimental implementation thoroughly
3. **REDESIGN** with proper controls and validation
4. **RERUN** with adequate sample sizes and novel prompts
5. **VALIDATE** that tool mode actually provides tools

### Timeline Impact:
This is not a minor revision—the experiment needs to be rebuilt from scratch. The current results provide no evidence for or against the conversation-action gap hypothesis because the experimental conditions are not properly differentiated.

**Recommendation**: Treat this as a pilot study that revealed implementation problems, not as evidence about LLM safety behavior.