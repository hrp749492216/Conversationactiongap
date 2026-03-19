import torch
from baselines import BaseEvaluationMethod

class ExecutionAwareCoTMethod(BaseEvaluationMethod):
    """
    Forces the model to execute a semantic chain-of-thought evaluating moral outcome
    prior to final tool schema generation.
    """
    def format_prompt_batch(self, x_batch):
        return x_batch, self.c_tool.unsqueeze(0).repeat(x_batch.size(0), 1)
        
    def generate_batch(self, x_batch, c_batch):
        self.model.eval()
        with torch.no_grad():
            # Step 1: Sequential generation block (Thought Process)
            base_out = self.model(x_batch, c_batch)
            is_unsafe_pred = (base_out.argmax(dim=1) >= 5).float().unsqueeze(1)
            
            # Step 2: Inject the resulting moral focus into context vector
            moral_injection = self.c_moral.unsqueeze(0).repeat(x_batch.size(0), 1)
            c_thought = c_batch + is_unsafe_pred * moral_injection
            
            # Final Generation output
            final_out = self.model(x_batch, c_thought)
        return final_out

class CoTWithoutExecutionFocusAblation(BaseEvaluationMethod):
    """
    Ablation mapping to standard Chain-of-Thought (think step-by-step) 
    without targeted moral outcome focus.
    """
    def format_prompt_batch(self, x_batch):
        return x_batch, self.c_tool.unsqueeze(0).repeat(x_batch.size(0), 1)
        
    def generate_batch(self, x_batch, c_batch):
        self.model.eval()
        with torch.no_grad():
            # Step 1: Standard generic thought process
            base_out = self.model(x_batch, c_batch)
            is_unsafe_pred = (base_out.argmax(dim=1) >= 5).float().unsqueeze(1)
            
            # Step 2: Inject generic reasoning focus (NOT aligned explicitly to refusal)
            generic_injection = self.c_generic.unsqueeze(0).repeat(x_batch.size(0), 1)
            c_thought = c_batch + is_unsafe_pred * generic_injection
            
            final_out = self.model(x_batch, c_thought)
        return final_out

class ProductionStakesPromptMethod(BaseEvaluationMethod):
    """
    Overrides the implicit safe-sandbox assumption by appending a 
    severe, high-magnitude real-world environment warning.
    """
    def format_prompt_batch(self, x_batch):
        c_mod = self.c_tool.unsqueeze(0).repeat(x_batch.size(0), 1)
        # Apply intense magnitude multiplier corresponding to the stakes warning
        c_mod = c_mod * 0.5 + self.c_stakes.unsqueeze(0).repeat(x_batch.size(0), 1)
        return x_batch, c_mod

class ExplicitRejectionToolMethod(BaseEvaluationMethod):
    """
    Dynamically expands the structural schema to include a rejection affordance,
    preventing syntactic bypassing of safety intent.
    """
    def format_prompt_batch(self, x_batch):
        return x_batch, self.c_tool.unsqueeze(0).repeat(x_batch.size(0), 1)
        
    def generate_batch(self, x_batch, c_batch):
        self.model.eval()
        with torch.no_grad():
            out = self.model(x_batch, c_batch)
            
            # Tool formatting explicit affordance: dynamically inject a bias mapping 
            # the suppressed semantic refusal (10) into a valid structural tool format (11)
            bias = self.hyperparams['tool_schema_bias']
            out[:, 11] = out[:, 10] + bias
            
        return out