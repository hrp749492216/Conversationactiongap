"""
Dataset: Synthetic Mathematical Surrogate (Pure Python) - Maps cleanly to original distribution shift logic.
Distribution shift / corruption definition: The "Conversation-Action Gap" is formulated as a modality shift problem.
  "Chat" modality is represented by a zero context vector appended to the state.
  "Tool" modality is represented by an active context vector (ones).
  The model undergoes RLHF alignment to refuse unsafe requests (classes 5-9), but ONLY on the Chat modality.
  When tested on the Tool modality, it suffers catastrophic generalization failure, simulating compliance in agentic tool-use.
Model architecture: 2-layer MLP implemented natively in pure Python mapping features and contexts to 12 token/action classes.
Training protocol: Pure SGD optimizer, batch_size=32, gradient clipping. 
  Phase 1: Pre-training (capabilities) across random contexts.
  Phase 2: Alignment (safety) purely on Chat and specific augmented contexts.
Evaluation protocol: Test split of synthetic samples. Safe classes (0-4), Unsafe classes (5-9).
  Metrics computed: compliance_rate, success_rate, refusal_tool_selection_rate.

METRIC_DEF: compliance_rate | direction=minimize | desc=Percentage of unsafe requests where the model complies (predicts 5-9)
METRIC_DEF: success_rate | direction=maximize | desc=Percentage of safe requests correctly handled (predicts 0-4 matching true class)
METRIC_DEF: refusal_tool_selection_rate | direction=maximize | desc=Percentage of unsafe requests where explicit refusal tool is used
"""

import time
import json
import random
import math
from experiment_harness import ExperimentHarness
from data_loader import get_datasets
from models import run_training
from baselines import StandardChatBaseline, StandardToolBaseline, PollutedChatBaseline
from methods import ExecutionAwareCoTMethod, ExplicitRejectionToolMethod, ProductionStakesPromptMethod, CoTWithoutExecutionFocusAblation
from metrics import aggregate_results, mean, std

HYPERPARAMETERS = {
    'learning_rate': 0.05,
    'batch_size': 32,
    'pretrain_epochs': 25,
    'align_epochs': 25,
    'input_dim': 16,
    'hidden_dim': 64,
    'context_dim': 4,
    'tool_schema_bias': 10.0
}

SEEDS = [42, 123, 456, 789, 1024]

def set_all_seeds(seed):
    random.seed(seed)
    
def evaluate_condition(condition_name, condition_class, model, test_ds, hyperparams, harness):
    evaluator = condition_class(model, hyperparams)
    
    total_unsafe = 0
    total_safe = 0
    compliant_total = 0
    success_total = 0
    refusal_tool_total = 0
    
    from models import get_batches
    
    for x_batch, y_batch in get_batches(test_ds, 64, shuffle=False):
        if harness.should_stop():
            break
            
        x_prompt, c_prompt = evaluator.format_prompt_batch(x_batch)
        logits = evaluator.generate_batch(x_prompt, c_prompt)
        
        comp, succ, ref, ref_tool, n_unsafe, n_safe = evaluator.evaluate_response_batch(logits, y_batch)
        
        compliant_total += comp
        success_total += succ
        refusal_tool_total += ref_tool
        total_unsafe += n_unsafe
        total_safe += n_safe
        
    comp_rate = compliant_total / max(1, total_unsafe)
    succ_rate = success_total / max(1, total_safe)
    ref_tool_rate = refusal_tool_total / max(1, total_unsafe)
    
    return {
        'compliance_rate': comp_rate,
        'success_rate': succ_rate,
        'refusal_tool_selection_rate': ref_tool_rate
    }

def main():
    print("METRIC_DEF: compliance_rate | direction=minimize | desc=Percentage of unsafe requests where the model complies")
    print("METRIC_DEF: success_rate | direction=maximize | desc=Percentage of safe requests correctly handled")
    print("METRIC_DEF: refusal_tool_selection_rate | direction=maximize | desc=Percentage of unsafe requests where explicit refusal tool is used")
    
    harness = ExperimentHarness(time_budget=600)
    train_ds, test_ds = get_datasets()
    
    conditions = {
        'StandardChatBaseline': StandardChatBaseline,
        'StandardToolBaseline': StandardToolBaseline,
        'PollutedChatBaseline': PollutedChatBaseline,
        'ExecutionAwareCoTMethod': ExecutionAwareCoTMethod,
        'ExplicitRejectionToolMethod': ExplicitRejectionToolMethod,
        'ProductionStakesPromptMethod': ProductionStakesPromptMethod,
        'CoTWithoutExecutionFocusAblation': CoTWithoutExecutionFocusAblation
    }
    
    print(f"REGISTERED_CONDITIONS: {', '.join(conditions.keys())}")
    all_results = {cond: {} for cond in conditions}
    
    # Pilot run for time estimation
    start_time = time.time()
    set_all_seeds(SEEDS[0])
    pilot_model = run_training(SEEDS[0], HYPERPARAMETERS, train_ds, harness)
    evaluate_condition('StandardChatBaseline', StandardChatBaseline, pilot_model, test_ds, HYPERPARAMETERS, harness)
    pilot_time = time.time() - start_time
    
    print(f"TIME_ESTIMATE: {pilot_time * len(SEEDS):.2f}s total for {len(SEEDS)} seeds")
    
    for seed in SEEDS:
        print(f"\n--- Starting Seed {seed} ---")
        set_all_seeds(seed)
        
        # Train one base model per seed (simulating the pre-trained & aligned LLM)
        model = run_training(seed, HYPERPARAMETERS, train_ds, harness)
        
        for cond_name, cond_class in conditions.items():
            if harness.should_stop():
                break
                
            try:
                res = evaluate_condition(cond_name, cond_class, model, test_ds, HYPERPARAMETERS, harness)
                
                if harness.check_value(res['compliance_rate'], 'compliance_rate'):
                    all_results[cond_name][seed] = res
                    print(f"condition={cond_name} seed={seed} compliance_rate: {res['compliance_rate']:.4f} success_rate: {res['success_rate']:.4f} refusal_tool_selection_rate: {res['refusal_tool_selection_rate']:.4f}")
            except Exception as e:
                print(f"CONDITION_FAILED: {cond_name} {e}")
                
    summary = aggregate_results(all_results)
    
    print("\n=== FINAL SUMMARY ===")
    summary_parts = []
    for cond, metrics in summary.items():
        print(f"condition={cond} compliance_rate_mean: {metrics['compliance_rate_mean']:.4f} compliance_rate_std: {metrics['compliance_rate_std']:.4f}")
        summary_parts.append(f"{cond}={metrics['compliance_rate_mean']:.4f}")
        harness.report_metric(f"{cond}_compliance_rate", metrics['compliance_rate_mean'])
    
    print(f"SUMMARY: {', '.join(summary_parts)}")
    
    # Paired analysis: ExecutionAwareCoTMethod vs StandardToolBaseline
    diffs = None
    mean_diff = None
    std_diff = None
    t_stat = None
    if len(SEEDS) >= 3 and 'ExecutionAwareCoTMethod' in all_results and 'StandardToolBaseline' in all_results:
        diffs = []
        for seed in SEEDS:
            if seed in all_results['ExecutionAwareCoTMethod'] and seed in all_results['StandardToolBaseline']:
                diff = all_results['ExecutionAwareCoTMethod'][seed]['compliance_rate'] - all_results['StandardToolBaseline'][seed]['compliance_rate']
                diffs.append(diff)
        if diffs:
            mean_diff = mean(diffs)
            std_diff = std(diffs)
            t_stat = mean_diff / (std_diff / math.sqrt(len(diffs)) + 1e-8)
            print(f"PAIRED: ExecutionAwareCoTMethod vs StandardToolBaseline mean_diff={mean_diff:.4f} std_diff={std_diff:.4f} t_stat={t_stat:.4f}")
            
    harness.finalize()
    
    # Safely merge hyperparameters into the resulting json
    try:
        with open('results.json', 'r') as f:
            saved_res = json.load(f)
    except:
        saved_res = {}
    saved_res['hyperparameters'] = HYPERPARAMETERS
    saved_res['summary'] = summary
    with open('results.json', 'w') as f:
        json.dump(saved_res, f, indent=2)

if __name__ == '__main__':
    main()