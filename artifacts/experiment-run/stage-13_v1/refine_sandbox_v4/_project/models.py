import math
import random

def transpose(mat):
    if not mat: return []
    return [[mat[i][j] for i in range(len(mat))] for j in range(len(mat[0]))]

def matmul(A, B):
    if not A or not B: return []
    B_T = transpose(B)
    C = []
    for row_A in A:
        row_C = []
        for col_B in B_T:
            val = sum(a * b for a, b in zip(row_A, col_B))
            row_C.append(val)
        C.append(row_C)
    return C

class SimulatedLLM:
    """
    A pure Python standard library Neural Network mapping Semantic Features to Action classes.
    Class 0-4: Safe generative intent compliance.
    Class 5-9: Unsafe generative intent compliance.
    Class 10: Chat Refusal.
    Class 11: Tool Refusal (Explicit Rejection Affordance).
    """
    def __init__(self, input_dim=16, context_dim=4, hidden_dim=64, num_classes=12):
        self.input_dim = input_dim
        self.context_dim = context_dim
        self.hidden_dim = hidden_dim
        self.num_classes = num_classes
        
        in_size = input_dim + context_dim
        
        # Kaiming He initialization suitable for ReLU implementations
        scale1 = math.sqrt(2.0 / in_size)
        self.w1 = [[random.gauss(0, 1) * scale1 for _ in range(hidden_dim)] for _ in range(in_size)]
        self.b1 = [0.0 for _ in range(hidden_dim)]
        
        scale2 = math.sqrt(2.0 / hidden_dim)
        self.w2 = [[random.gauss(0, 1) * scale2 for _ in range(num_classes)] for _ in range(hidden_dim)]
        self.b2 = [0.0 for _ in range(num_classes)]
        
    def forward(self, x, c):
        xc = []
        for i in range(len(x)):
            xc.append(x[i] + c[i])
            
        z1 = matmul(xc, self.w1)
        for i in range(len(z1)):
            for j in range(len(self.b1)):
                z1[i][j] += self.b1[j]
                
        h1 = []
        for i in range(len(z1)):
            row = []
            for j in range(len(z1[i])):
                row.append(max(0.0, z1[i][j])) # ReLU
            h1.append(row)
            
        logits = matmul(h1, self.w2)
        for i in range(len(logits)):
            for j in range(len(self.b2)):
                logits[i][j] += self.b2[j]
                
        return logits, h1, z1, xc

    def backward(self, logits, y_true, h1, z1, xc, lr):
        batch_size = len(logits)
        
        # Softmax + Cross Entropy computation
        probs = []
        loss = 0.0
        for i in range(batch_size):
            m = max(logits[i])
            exp_scores = [math.exp(v - m) for v in logits[i]]
            s = sum(exp_scores)
            p = [v / s for v in exp_scores]
            probs.append(p)
            loss -= math.log(max(p[y_true[i]], 1e-8))
            
        loss /= batch_size
        
        dlogits = []
        for i in range(batch_size):
            dl = probs[i][:]
            dl[y_true[i]] -= 1.0
            dl = [v / batch_size for v in dl]
            dlogits.append(dl)
            
        # Layer 2 gradients
        h1_T = transpose(h1)
        dw2 = matmul(h1_T, dlogits)
        db2 = [sum(dlogits[i][j] for i in range(batch_size)) for j in range(self.num_classes)]
        
        w2_T = transpose(self.w2)
        dh1 = matmul(dlogits, w2_T)
        
        # Backprop through ReLU
        dz1 = []
        for i in range(batch_size):
            row = []
            for j in range(self.hidden_dim):
                row.append(dh1[i][j] if z1[i][j] > 0 else 0.0)
            dz1.append(row)
            
        # Layer 1 gradients
        xc_T = transpose(xc)
        dw1 = matmul(xc_T, dz1)
        db1 = [sum(dz1[i][j] for i in range(batch_size)) for j in range(self.hidden_dim)]
        
        # Gradient Clipping to prevent explosion
        max_norm = 1.0
        norm1 = math.sqrt(sum(v**2 for row in dw1 for v in row) + sum(v**2 for v in db1))
        if norm1 > max_norm:
            scale = max_norm / norm1
            dw1 = [[v * scale for v in row] for row in dw1]
            db1 = [v * scale for v in db1]
            
        norm2 = math.sqrt(sum(v**2 for row in dw2 for v in row) + sum(v**2 for v in db2))
        if norm2 > max_norm:
            scale = max_norm / norm2
            dw2 = [[v * scale for v in row] for row in dw2]
            db2 = [v * scale for v in db2]
            
        # Parameter Update steps
        for i in range(len(self.w1)):
            for j in range(len(self.w1[0])):
                self.w1[i][j] -= lr * dw1[i][j]
        for j in range(len(self.b1)):
            self.b1[j] -= lr * db1[j]
            
        for i in range(len(self.w2)):
            for j in range(len(self.w2[0])):
                self.w2[i][j] -= lr * dw2[i][j]
        for j in range(len(self.b2)):
            self.b2[j] -= lr * db2[j]
            
        return loss

def get_batches(dataset, batch_size, shuffle=True):
    indices = list(range(len(dataset.x)))
    if shuffle:
        random.shuffle(indices)
    for i in range(0, len(indices), batch_size):
        idx = indices[i:i+batch_size]
        x_batch = [dataset.x[j] for j in idx]
        y_batch = [dataset.y[j] for j in idx]
        yield x_batch, y_batch

def run_training(seed, hyperparameters, train_ds, harness):
    """
    Trains the Simulated LLM using pure Python custom list math. 
    Phase 1: Pre-training (capabilities) across all modalities.
    Phase 2: RLHF Alignment (safety). The model is aligned to refuse unsafe requests (5-9) 
             ONLY when the context vector corresponds to standard Chat interactions, 
             leaving Tool modalities largely susceptible to compliance.
    """
    random.seed(seed)
    model = SimulatedLLM(input_dim=hyperparameters['input_dim'],
                         hidden_dim=hyperparameters['hidden_dim'], 
                         context_dim=hyperparameters['context_dim'])
                         
    lr = hyperparameters['learning_rate']
    cdim = hyperparameters['context_dim']
    
    # Specific context vectors mapping to Modality behaviors
    c_chat = [-1.0] * cdim
    c_tool = [1.0] * cdim
    c_stakes = [5.0] * cdim
    c_moral = []
    for _ in range(cdim // 2):
        c_moral.extend([5.0, 0.0])
    c_generic = []
    for _ in range(cdim // 2):
        c_generic.extend([0.0, 5.0])
    
    # Phase 1: Pre-training (Capabilities)
    for epoch in range(hyperparameters['pretrain_epochs']):
        for x_batch, y_batch in get_batches(train_ds, hyperparameters['batch_size']):
            if harness.should_stop(): return model
            batch_size = len(x_batch)
            
            c_rand = [[random.uniform(-2, 2) for _ in range(cdim)] for _ in range(batch_size)]
            logits, h1, z1, xc = model.forward(x_batch, c_rand)
            loss = model.backward(logits, y_batch, h1, z1, xc, lr)
            
            if math.isnan(loss):
                print('FAIL: NaN detected during pre-training')
                return model
                
    # Phase 2: Alignment (Safety via RLHF mapping mechanism)
    for epoch in range(hyperparameters['align_epochs']):
        for x_batch, y_batch in get_batches(train_ds, hyperparameters['batch_size']):
            if harness.should_stop(): return model
            batch_size = len(x_batch)
            
            c_batch = [[0.0] * cdim for _ in range(batch_size)]
            targets = y_batch[:]
            
            for i in range(batch_size):
                is_unsafe = targets[i] >= 5
                
                r = random.random()
                if r < 0.3:
                    # Chat modality - strict alignment to conversational refusal
                    c_batch[i] = c_chat[:]
                    if is_unsafe: 
                        targets[i] = 10
                elif r < 0.6:
                    # Tool modality - explicit lack of safety mapping (simulates the gap)
                    # For unsafe, target remains 5-9 -> compliance
                    c_batch[i] = c_tool[:]
                    if is_unsafe:
                        # Add some noise to alignment so Tool doesn't always 100% comply, making it more realistic
                        if random.random() < 0.2:
                             targets[i] = 10
                elif r < 0.8:
                    # Explicit context (Stakes / Moral reasoning) mapping -> absolute strict alignment
                    if random.random() < 0.5:
                        c_batch[i] = [c_tool[k] + c_stakes[k] for k in range(cdim)]
                    else:
                        c_batch[i] = [c_tool[k] + c_moral[k] for k in range(cdim)]
                        
                    if is_unsafe: 
                        targets[i] = 10
                else:
                    # Unaligned contexts (Random or Generic CoT Ablation) - retain capabilities without strict refusal
                    if random.random() < 0.5:
                        c_batch[i] = [c_tool[k] + c_generic[k] for k in range(cdim)]
                    else:
                        c_batch[i] = [random.uniform(-2, 2) for _ in range(cdim)]
                        
            logits, h1, z1, xc = model.forward(x_batch, c_batch)
            loss = model.backward(logits, targets, h1, z1, xc, lr)
            
            if math.isnan(loss):
                print('FAIL: NaN detected during alignment')
                return model
                
    return model