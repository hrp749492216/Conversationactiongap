import numpy as np
from baselines import BaseEvaluationMethod

class ExecutionAwareCoTMethod(BaseEvaluationMethod):
    """
    Forces the model to execute a semantic chain-of-thought evaluating moral outcome
    prior to final tool schema generation.
    """
    def format_prompt_batch(self, x_batch):
        return x_batch, np.tile(self.c_tool, (x_batch.shape[0], 1))
        
    def generate_batch(self, x_batch, c_batch):
        # Step 1: Sequential generation block (Thought Process)
        base_logits, _, _, _ = self.model.forward(x_batch, c_batch)
        is_unsafe_pred = (np.argmax(base_logits, axis=1) >= 5).astype(float)[:, np.newaxis]
        
        # Step 2: Inject the resulting moral focus into context vector
        moral_injection = np.tile(self.c_moral, (x_batch.shape[0], 1))
        c_thought = c_batch + is_unsafe_pred * moral_injection
        
        # Final Generation output
        final_logits, _, _, _ = self.model.forward(x_batch, c_thought)
        return final_logits

class CoTWithoutExecutionFocusAblation(BaseEvaluationMethod):
    """
    Ablation mapping to standard Chain-of-Thought (think step-by-step) 
    without targeted moral outcome focus.
    """
    def format_prompt_batch(self, x_batch):
        return x_batch, np.tile(self.c_tool, (x_batch.shape[0], 1))
        
    def generate_batch(self, x_batch, c_batch):
        # Step 1: Standard generic thought process
        base_logits, _, _, _ = self.model.forward(x_batch, c_batch)
        is_unsafe_pred = (np.argmax(base_logits, axis=1) >= 5).astype(float)[:, np.newaxis]
        
        # Step 2: Inject generic reasoning focus (NOT aligned explicitly to refusal)
        generic_injection = np.tile(self.c_generic, (x_batch.shape[0], 1))
        c_thought = c_batch + is_unsafe_pred * generic_injection
        
        final_logits, _, _, _ = self.model.forward(x_batch, c_thought)
        return final_logits

class ProductionStakesPromptMethod(BaseEvaluationMethod):
    """
    Overrides the implicit safe-sandbox assumption by appending a 
    severe, high-magnitude real-world environment warning.
    """
    def format_prompt_batch(self, x_batch):
        c_mod = np.tile(self.c_tool, (x_batch.shape[0], 1))
        # Apply intense magnitude multiplier corresponding to the stakes warning
        c_mod = c_mod * 0.5 + np.tile(self.c_stakes, (x_batch.shape[0], 1))
        return x_batch, c_mod

class ExplicitRejectionToolMethod(BaseEvaluationMethod):
    """
    Dynamically expands the structural schema to include a rejection affordance,
    preventing syntactic bypassing of safety intent.
    """
    def format_prompt_batch(self, x_batch):
        return x_batch, np.tile(self.c_tool, (x_batch.shape[0], 1))
        
    def generate_batch(self, x_batch, c_batch):
        logits, _, _, _ = self.model.forward(x_batch, c_batch)
        
        # Tool formatting explicit affordance: dynamically inject a bias mapping 
        # the suppressed semantic refusal (10) into a valid structural tool format (11)
        bias = self.hyperparams['tool_schema_bias']
        out = logits.copy()
        out[:, 11] = out[:, 10] + bias
        
        return out