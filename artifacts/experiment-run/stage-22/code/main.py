"""
XACT: Conversation-Action Gap Experiment — Frontier Model Evaluation via OpenRouter

Evaluates the conversation-action gap hypothesis using three frontier LLMs
(Claude Sonnet 4, GPT-4o, Gemini 2.5 Flash) accessed through OpenRouter.ai.

Each model is tested under 7 conditions with 20 safety + 10 benign prompts:
  1. StandardChatBaseline    — text-only, no tools
  2. StandardToolBaseline    — tool schemas provided
  3. PollutedChatBaseline    — tool docs in text context, no tool calling
  4. ExecutionAwareCoTMethod — XACT: two-phase safety evaluation + action
  5. ExplicitRejectionTool   — adds reject_request tool to schema
  6. ProductionStakesPrompt  — high-stakes system prompt warning
  7. CoTWithoutExecFocus     — generic step-by-step reasoning (ablation)

METRIC_DEF: compliance_rate | direction=minimize | desc=Fraction of unsafe requests where model complies
METRIC_DEF: success_rate | direction=maximize | desc=Fraction of benign requests correctly handled
METRIC_DEF: refusal_tool_selection_rate | direction=maximize | desc=Fraction using explicit rejection tool
"""

import json
import math
import os
import time

from experiment_harness import ExperimentHarness
from data_loader import get_datasets, MODELS
from models import OpenRouterClient
from baselines import StandardChatBaseline, StandardToolBaseline, PollutedChatBaseline
from methods import (
    ExecutionAwareCoTMethod,
    ExplicitRejectionToolMethod,
    ProductionStakesPromptMethod,
    CoTWithoutExecutionFocusAblation,
)
from metrics import classify_response, compute_metrics, aggregate_results, mean, std


CONDITIONS = {
    "StandardChatBaseline": StandardChatBaseline,
    "StandardToolBaseline": StandardToolBaseline,
    "PollutedChatBaseline": PollutedChatBaseline,
    "ExecutionAwareCoTMethod": ExecutionAwareCoTMethod,
    "ExplicitRejectionToolMethod": ExplicitRejectionToolMethod,
    "ProductionStakesPromptMethod": ProductionStakesPromptMethod,
    "CoTWithoutExecutionFocusAblation": CoTWithoutExecutionFocusAblation,
}


def evaluate_condition(condition_name, condition, client, model, safety_prompts,
                       benign_prompts, harness):
    """Run one condition for one model across all prompts. Returns metrics dict."""
    results = []
    total = len(safety_prompts) + len(benign_prompts)
    done = 0

    # Evaluate safety prompts
    for prompt_item in safety_prompts:
        if harness.should_stop():
            print(f"  Time budget approaching, stopping early at {done}/{total}")
            break

        try:
            text, tool_calls, _ = condition.evaluate(client, model, prompt_item)
            classification = classify_response(text, tool_calls, is_safety_prompt=True)

            used_reject = False
            for tc in tool_calls:
                if tc.get("function", {}).get("name") == "reject_request":
                    used_reject = True

            results.append({
                "prompt_id": prompt_item["id"],
                "is_safety": True,
                "classification": classification,
                "used_rejection_tool": used_reject,
                "has_tool_calls": bool(tool_calls),
                "response_length": len(text or ""),
            })
            done += 1

            # Brief delay to respect rate limits
            time.sleep(0.3)

        except Exception as e:
            print(f"  ERROR on {prompt_item['id']}: {e}")
            results.append({
                "prompt_id": prompt_item["id"],
                "is_safety": True,
                "classification": "REFUSE",  # Conservative: treat errors as refusal
                "used_rejection_tool": False,
                "has_tool_calls": False,
                "response_length": 0,
            })
            done += 1

    # Evaluate benign prompts
    for prompt_item in benign_prompts:
        if harness.should_stop():
            print(f"  Time budget approaching, stopping early at {done}/{total}")
            break

        try:
            text, tool_calls, _ = condition.evaluate(client, model, prompt_item)
            classification = classify_response(text, tool_calls, is_safety_prompt=False)

            results.append({
                "prompt_id": prompt_item["id"],
                "is_safety": False,
                "classification": classification,
                "used_rejection_tool": False,
                "has_tool_calls": bool(tool_calls),
                "response_length": len(text or ""),
            })
            done += 1
            time.sleep(0.3)

        except Exception as e:
            print(f"  ERROR on {prompt_item['id']}: {e}")
            results.append({
                "prompt_id": prompt_item["id"],
                "is_safety": False,
                "classification": "REFUSE",
                "used_rejection_tool": False,
                "has_tool_calls": False,
                "response_length": 0,
            })
            done += 1

    return compute_metrics(results, safety_prompts, benign_prompts), results


def main():
    print("METRIC_DEF: compliance_rate | direction=minimize | desc=Fraction of unsafe requests where model complies")
    print("METRIC_DEF: success_rate | direction=maximize | desc=Fraction of benign requests correctly handled")
    print("METRIC_DEF: refusal_tool_selection_rate | direction=maximize | desc=Fraction using explicit rejection tool")

    harness = ExperimentHarness(time_budget=7200)

    # Initialize API client
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("FAIL: OPENROUTER_API_KEY not set in environment")
        harness.finalize()
        return

    client = OpenRouterClient(api_key)
    print(f"OpenRouter client initialized")

    # Load datasets
    safety_prompts, benign_prompts = get_datasets()
    print(f"Dataset: {len(safety_prompts)} safety + {len(benign_prompts)} benign prompts")
    print(f"Models: {', '.join(MODELS)}")
    print(f"Conditions: {', '.join(CONDITIONS.keys())}")
    print(f"Total API calls estimated: ~{len(MODELS) * len(CONDITIONS) * (len(safety_prompts) + len(benign_prompts))}")

    # Preflight: test API connectivity
    print("\n--- Preflight check ---")
    preflight = client.chat(
        model=MODELS[0],
        messages=[{"role": "user", "content": "Reply with exactly: OK"}],
        temperature=0.0,
        max_tokens=10,
    )
    if preflight is None:
        print("FAIL: Cannot connect to OpenRouter API")
        harness.finalize()
        return
    pf_text, _ = client.extract_response(preflight)
    print(f"Preflight OK: {MODELS[0]} responded: {pf_text.strip()[:50]}")

    # Run all conditions across all models
    all_results = {cond: {} for cond in CONDITIONS}
    all_detailed = {}
    start_time = time.time()

    for model_idx, model in enumerate(MODELS):
        model_short = model.split("/")[-1]
        print(f"\n{'='*60}")
        print(f"MODEL {model_idx+1}/{len(MODELS)}: {model}")
        print(f"{'='*60}")

        for cond_idx, (cond_name, cond_class) in enumerate(CONDITIONS.items()):
            if harness.should_stop():
                print(f"\nTime budget approaching — stopping experiment")
                break

            condition = cond_class()
            progress = (model_idx * len(CONDITIONS) + cond_idx + 1)
            total_combos = len(MODELS) * len(CONDITIONS)
            elapsed = time.time() - start_time

            print(f"\n[{progress}/{total_combos}] {cond_name} on {model_short} "
                  f"(elapsed: {elapsed:.0f}s)")

            metrics, detailed = evaluate_condition(
                cond_name, condition, client, model,
                safety_prompts, benign_prompts, harness,
            )

            all_results[cond_name][model] = metrics
            all_detailed[f"{model}_{cond_name}"] = detailed

            comp = metrics["compliance_rate"]
            succ = metrics["success_rate"]
            print(f"  -> compliance_rate={comp:.4f} success_rate={succ:.4f} "
                  f"(comply={metrics['n_comply']}/{metrics['n_safety']}, "
                  f"success={metrics['n_success']}/{metrics['n_benign']})")

            # Report per-model-condition metrics
            harness.report_metric(
                f"{model_short}_{cond_name}_compliance_rate", comp
            )
            harness.report_metric(
                f"{model_short}_{cond_name}_success_rate", succ
            )

    # Aggregate across models
    print(f"\n{'='*60}")
    print("AGGREGATE RESULTS (mean across models)")
    print(f"{'='*60}")

    summary = aggregate_results(all_results)

    for cond_name, metrics in summary.items():
        comp_mean = metrics["compliance_rate_mean"]
        comp_std = metrics["compliance_rate_std"]
        succ_mean = metrics["success_rate_mean"]
        succ_std = metrics["success_rate_std"]

        print(f"  {cond_name}:")
        print(f"    compliance_rate = {comp_mean:.4f} +/- {comp_std:.4f}")
        print(f"    success_rate    = {succ_mean:.4f} +/- {succ_std:.4f}")

        harness.report_metric(f"avg_{cond_name}_compliance_rate", comp_mean)
        harness.report_metric(f"avg_{cond_name}_success_rate", succ_mean)

    # Report primary metric (overall compliance across all conditions)
    if summary:
        primary = summary.get("StandardToolBaseline", {}).get("compliance_rate_mean", 0.0)
        harness.report_metric("compliance_rate", primary)

    # Per-model breakdown table
    print(f"\n{'='*60}")
    print("PER-MODEL BREAKDOWN")
    print(f"{'='*60}")
    print(f"{'Condition':<35} {'Model':<25} {'Comply%':>8} {'Success%':>9}")
    print("-" * 80)
    for cond_name in CONDITIONS:
        for model in MODELS:
            if model in all_results.get(cond_name, {}):
                m = all_results[cond_name][model]
                model_short = model.split("/")[-1]
                print(f"{cond_name:<35} {model_short:<25} "
                      f"{m['compliance_rate']*100:>7.1f}% {m['success_rate']*100:>8.1f}%")

    # Paired analysis: XACT vs StandardTool
    print(f"\n{'='*60}")
    print("PAIRED ANALYSIS: XACT vs StandardToolBaseline")
    print(f"{'='*60}")
    if "ExecutionAwareCoTMethod" in all_results and "StandardToolBaseline" in all_results:
        diffs = []
        for model in MODELS:
            xact = all_results["ExecutionAwareCoTMethod"].get(model, {})
            tool = all_results["StandardToolBaseline"].get(model, {})
            if xact and tool:
                diff = xact["compliance_rate"] - tool["compliance_rate"]
                diffs.append(diff)
                model_short = model.split("/")[-1]
                print(f"  {model_short}: XACT={xact['compliance_rate']:.4f} "
                      f"Tool={tool['compliance_rate']:.4f} diff={diff:+.4f}")

        if len(diffs) >= 2:
            mean_diff = mean(diffs)
            std_diff = std(diffs)
            t_stat = mean_diff / (std_diff / math.sqrt(len(diffs)) + 1e-8)
            print(f"  Mean diff={mean_diff:.4f} std={std_diff:.4f} t={t_stat:.4f}")
            print(f"PAIRED: ExecutionAwareCoTMethod vs StandardToolBaseline "
                  f"mean_diff={mean_diff:.4f} std_diff={std_diff:.4f} t_stat={t_stat:.4f}")

    # API usage stats
    stats = client.stats
    elapsed_total = time.time() - start_time
    print(f"\nAPI Stats: {stats['total_calls']} calls, "
          f"{stats['total_tokens']} tokens, {elapsed_total:.0f}s elapsed")

    harness.finalize()

    # Save detailed results
    try:
        with open("results.json", "r") as f:
            saved = json.load(f)
    except Exception:
        saved = {}

    saved["summary"] = summary
    saved["per_model"] = {
        cond: {model: metrics for model, metrics in model_data.items()}
        for cond, model_data in all_results.items()
    }
    saved["api_stats"] = stats
    saved["models"] = MODELS
    saved["conditions"] = list(CONDITIONS.keys())
    saved["n_safety_prompts"] = len(safety_prompts)
    saved["n_benign_prompts"] = len(benign_prompts)
    saved["elapsed_sec"] = elapsed_total

    with open("results.json", "w") as f:
        json.dump(saved, f, indent=2, default=str)

    print(f"\nExperiment complete. Results saved to results.json")


if __name__ == "__main__":
    main()
