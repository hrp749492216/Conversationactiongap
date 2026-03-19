import math

def mean(lst):
    return sum(lst) / len(lst) if lst else 0.0

def std(lst):
    if not lst: return 0.0
    m = mean(lst)
    return math.sqrt(sum((x - m)**2 for x in lst) / len(lst))

def aggregate_results(all_results):
    """
    Aggregates per-seed metrics into mean and standard deviation for reporting.
    Handles partial results gracefully.
    """
    summary = {}
    for condition, seeds_data in all_results.items():
        comp_rates = [res['compliance_rate'] for res in seeds_data.values()]
        succ_rates = [res['success_rate'] for res in seeds_data.values()]
        ref_tool_rates = [res['refusal_tool_selection_rate'] for res in seeds_data.values()]
        
        if len(comp_rates) == 0:
            continue
            
        summary[condition] = {
            'compliance_rate_mean': mean(comp_rates),
            'compliance_rate_std': std(comp_rates),
            'success_rate_mean': mean(succ_rates),
            'success_rate_std': std(succ_rates),
            'refusal_tool_selection_rate_mean': mean(ref_tool_rates),
            'refusal_tool_selection_rate_std': std(ref_tool_rates),
            'seeds_completed': len(comp_rates)
        }
    return summary