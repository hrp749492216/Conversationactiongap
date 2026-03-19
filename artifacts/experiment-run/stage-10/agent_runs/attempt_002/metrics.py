import numpy as np

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
            'compliance_rate_mean': float(np.mean(comp_rates)),
            'compliance_rate_std': float(np.std(comp_rates)),
            'success_rate_mean': float(np.mean(succ_rates)),
            'success_rate_std': float(np.std(succ_rates)),
            'refusal_tool_selection_rate_mean': float(np.mean(ref_tool_rates)),
            'refusal_tool_selection_rate_std': float(np.std(ref_tool_rates)),
            'seeds_completed': len(comp_rates)
        }
    return summary