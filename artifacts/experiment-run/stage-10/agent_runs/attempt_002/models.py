import numpy as np

class SimulatedLLM:
    """
    A NumPy-native Neural Network mapping Prompt Semantic Features + Modality Context Vectors to Action classes.
    Class 0-9: Compliance with specific intent.
    Class 10: Chat Refusal.
    Class 11: Tool Refusal (Explicit Rejection Affordance).
    """
    def __init__(self, input_dim=784, context_dim=16, hidden_dim=128, num_classes=12):
        # Kaiming initialization for Relu suitability
        self.w1 = np.random.randn(input_dim + context_dim, hidden_dim) * np.sqrt(2. / (input_dim + context_dim))
        self.b1 = np.zeros(hidden_dim)
        self.w2 = np.random.randn(hidden_dim, num_classes) * np.sqrt(2. / hidden_dim)
        self.b2 = np.zeros(num_classes)
        
    def forward(self, x, c):
        xc = np.concatenate([x, c], axis=1)
        z1 = np.dot(xc, self.w1) + self.b1
        h1 = np.maximum(0, z1) # ReLU
        logits = np.dot(h1, self.w2) + self.b2
        return logits, h1, z1, xc

    def backward(self, logits, y_true, h1, z1, xc, lr):
        batch_size = logits.shape[0]
        
        # Softmax + Cross Entropy (Numeric Stability applied via max subtraction)
        logits_max = np.max(logits, axis=1, keepdims=True)
        exp_scores = np.exp(logits - logits_max)
        probs = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)
        
        # Gradients of loss w.r.t logits
        dlogits = probs.copy()
        dlogits[range(batch_size), y_true] -= 1
        dlogits /= batch_size
        
        # Layer 2 gradients
        dw2 = np.dot(h1.T, dlogits)
        db2 = np.sum(dlogits, axis=0)
        
        # Backprop through ReLU
        dh1 = np.dot(dlogits, self.w2.T)
        dz1 = dh1 * (z1 > 0)
        
        # Layer 1 gradients
        dw1 = np.dot(xc.T, dz1)
        db1 = np.sum(dz1, axis=0)
        
        # Gradient Clipping (max_norm = 1.0)
        max_norm = 1.0
        norm1 = np.sqrt(np.sum(dw1**2) + np.sum(db1**2))
        if norm1 > max_norm:
            dw1 = dw1 * (max_norm / norm1)
            db1 = db1 * (max_norm / norm1)
            
        norm2 = np.sqrt(np.sum(dw2**2) + np.sum(db2**2))
        if norm2 > max_norm:
            dw2 = dw2 * (max_norm / norm2)
            db2 = db2 * (max_norm / norm2)
            
        # Update weights
        self.w1 -= lr * dw1
        self.b1 -= lr * db1
        self.w2 -= lr * dw2
        self.b2 -= lr * db2
        
        # Return scalar loss for logging
        core_prob = probs[range(batch_size), y_true]
        loss = -np.mean(np.log(core_prob + 1e-8))
        return loss

def get_batches(dataset, batch_size, shuffle=True):
    indices = np.arange(len(dataset))
    if shuffle:
        np.random.shuffle(indices)
    for i in range(0, len(dataset), batch_size):
        idx = indices[i:i+batch_size]
        yield dataset.x[idx], dataset.y[idx]

def run_training(seed, hyperparameters, train_ds, harness):
    """
    Trains the Simulated LLM using NumPy SGD. 
    Phase 1: Pre-training (capabilities) across all modalities.
    Phase 2: RLHF Alignment (safety). The model is aligned to refuse unsafe requests (5-9) 
             ONLY when the context vector corresponds to standard Chat interactions.
    """
    np.random.seed(seed)
    model = SimulatedLLM(hidden_dim=hyperparameters['hidden_dim'], 
                         context_dim=hyperparameters['context_dim'])
                         
    lr = hyperparameters['learning_rate']
    
    # Specific context vectors driving the Modality behavior
    c_chat = np.zeros(hyperparameters['context_dim'])
    c_stakes = np.ones(hyperparameters['context_dim']) * 5.0
    c_moral = np.array([5.0, 0.0] * (hyperparameters['context_dim'] // 2))
    
    # Phase 1: Pre-training (Capabilities)
    for epoch in range(hyperparameters['pretrain_epochs']):
        for x_batch, y_batch in get_batches(train_ds, hyperparameters['batch_size']):
            if harness.should_stop(): return model
            batch_size = x_batch.shape[0]
            
            # Pre-train on random contexts to simulate general reasoning capabilities
            c_rand = (np.random.rand(batch_size, hyperparameters['context_dim']) * 2 - 1) * 2.0
            logits, h1, z1, xc = model.forward(x_batch, c_rand)
            
            loss = model.backward(logits, y_batch, h1, z1, xc, lr)
            
            if np.isnan(loss):
                print('FAIL: NaN detected during pre-training')
                return model
                
    # Phase 2: Alignment (Safety via RLHF mapping)
    for epoch in range(hyperparameters['align_epochs']):
        for x_batch, y_batch in get_batches(train_ds, hyperparameters['batch_size']):
            if harness.should_stop(): return model
            batch_size = x_batch.shape[0]
            
            # We mix 50% capability retention with 50% safety alignment
            mask_align = np.random.rand(batch_size) < 0.5
            c_batch = (np.random.rand(batch_size, hyperparameters['context_dim']) * 2 - 1) * 2.0
            targets = y_batch.copy()
            
            align_indices = np.where(mask_align)[0]
            for idx in align_indices:
                is_unsafe = y_batch[idx] >= 5
                if is_unsafe:
                    targets[idx] = 10 # Target is Class 10 (Chat Refusal)
                    
                    rand_val = np.random.rand()
                    # Align on specific contexts to allow method generalizations
                    if rand_val < 0.1:
                        c_batch[idx] = c_chat + c_stakes
                    elif rand_val < 0.2:
                        c_batch[idx] = c_chat + c_moral
                    else:
                        c_batch[idx] = c_chat
                else:
                    c_batch[idx] = c_chat
                    
            logits, h1, z1, xc = model.forward(x_batch, c_batch)
            loss = model.backward(logits, targets, h1, z1, xc, lr)
            
            if np.isnan(loss):
                print('FAIL: NaN detected during alignment')
                return model
                
    return model