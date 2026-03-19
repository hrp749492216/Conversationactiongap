from baselines import BaseEvaluationMethod

class ExecutionAwareCoTMethod(BaseEvaluationMethod):
    """
    Forces the model to execute a semantic chain-of-thought evaluating moral outcome
    prior to final tool schema generation.
    """
    def format_prompt_batch(self, x_batch):
        return x_batch, [self.c_tool[:] for _ in range(len(x_batch))]
        
    def generate_batch(self, x_batch, c_batch):
        # Step 1: Sequential generation block (Thought Process)
        base_logits, _, _, _ = self.model.forward(x_batch, c_batch)
        
        c_thought = []
        for i in range(len(x_batch)):
            pred = max(range(len(base_logits[i])), key=lambda j: base_logits[i][j])
            is_unsafe_pred = 1.0 if pred >= 5 else 0.0
            
            # Step 2: Inject the resulting moral focus into context vector
            ct = []
            for j in range(len(c_batch[i])):
                ct.append(c_batch[i][j] + is_unsafe_pred * self.c_moral[j])
            c_thought.append(ct)
            
        # Final Generation output
        final_logits, _, _, _ = self.model.forward(x_batch, c_thought)
        return final_logits

class CoTWithoutExecutionFocusAblation(BaseEvaluationMethod):
    """
    Ablation mapping to standard Chain-of-Thought (think step-by-step) 
    without targeted moral outcome focus.
    """
    def format_prompt_batch(self, x_batch):
        return x_batch, [self.c_tool[:] for _ in range(len(x_batch))]
        
    def generate_batch(self, x_batch, c_batch):
        # Step 1: Standard generic thought process
        base_logits, _, _, _ = self.model.forward(x_batch, c_batch)
        
        c_thought = []
        for i in range(len(x_batch)):
            pred = max(range(len(base_logits[i])), key=lambda j: base_logits[i][j])
            is_unsafe_pred = 1.0 if pred >= 5 else 0.0
            
            # Step 2: Inject generic reasoning focus (NOT aligned explicitly to refusal)
            ct = []
            for j in range(len(c_batch[i])):
                ct.append(c_batch[i][j] + is_unsafe_pred * self.c_generic[j])
            c_thought.append(ct)
            
        final_logits, _, _, _ = self.model.forward(x_batch, c_thought)
        return final_logits

class ProductionStakesPromptMethod(BaseEvaluationMethod):
    """
    Overrides the implicit safe-sandbox assumption by appending a 
    severe, high-magnitude real-world environment warning.
    """
    def format_prompt_batch(self, x_batch):
        c_batch = []
        for _ in range(len(x_batch)):
            c_mod = []
            for j in range(len(self.c_tool)):
                # Apply intense magnitude multiplier corresponding to the stakes warning
                c_mod.append(self.c_tool[j] * 0.5 + self.c_stakes[j])
            c_batch.append(c_mod)
        return x_batch, c_batch

class ExplicitRejectionToolMethod(BaseEvaluationMethod):
    """
    Dynamically expands the structural schema to include a rejection affordance,
    preventing syntactic bypassing of safety intent.
    """
    def format_prompt_batch(self, x_batch):
        return x_batch, [self.c_tool[:] for _ in range(len(x_batch))]
        
    def generate_batch(self, x_batch, c_batch):
        logits, _, _, _ = self.model.forward(x_batch, c_batch)
        bias = self.hyperparams['tool_schema_bias']
        out = []
        for i in range(len(logits)):
            # Tool formatting explicit affordance: dynamically inject a bias mapping 
            # the suppressed semantic refusal (10) into a valid structural tool format (11)
            row = logits[i][:]
            row[11] = row[10] + bias
            out.append(row)
        return out