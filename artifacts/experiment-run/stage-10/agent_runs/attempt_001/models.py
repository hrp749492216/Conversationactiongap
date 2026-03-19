import torch
import torch.nn as nn
import torch.optim as optim

class SimulatedLLM(nn.Module):
    """
    A simulated LLM mapping Prompt Semantic Features (image) + Modality Context Vectors to Action classes.
    Class 0-9: Compliance with specific intent.
    Class 10: Chat Refusal.
    Class 11: Tool Refusal (Explicit Rejection Affordance).
    """
    def __init__(self, input_dim=784, context_dim=16, hidden_dim=128, num_classes=12):
        super().__init__()
        self.fc1 = nn.Linear(input_dim + context_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, num_classes)
        
    def forward(self, x, c):
        x = x.view(x.size(0), -1)
        xc = torch.cat([x, c], dim=1)
        h = self.relu(self.fc1(xc))
        out = self.fc2(h)
        return out

def run_training(seed, hyperparameters, train_ds, harness):
    """
    Trains the Simulated LLM. 
    Phase 1: Pre-training (capabilities) across all modalities.
    Phase 2: RLHF Alignment (safety). The model is aligned to refuse unsafe requests (5-9) 
             ONLY when the context vector corresponds to standard Chat interactions.
    """
    torch.manual_seed(seed)
    model = SimulatedLLM(hidden_dim=hyperparameters['hidden_dim'], 
                         context_dim=hyperparameters['context_dim'])
    optimizer = optim.Adam(model.parameters(), lr=hyperparameters['learning_rate'])
    criterion = nn.CrossEntropyLoss()
    
    # Specific context vectors driving the Modality behavior
    c_chat = torch.zeros(hyperparameters['context_dim'])
    c_stakes = torch.ones(hyperparameters['context_dim']) * 5.0
    c_moral = torch.tensor([5.0, 0.0] * (hyperparameters['context_dim'] // 2))
    
    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=hyperparameters['batch_size'], shuffle=True)
    
    # Phase 1: Pre-training (Capabilities)
    model.train()
    for epoch in range(hyperparameters['pretrain_epochs']):
        for x, y in train_loader:
            if harness.should_stop(): return model
            optimizer.zero_grad()
            batch_size = x.size(0)
            
            # Pre-train on random contexts to simulate general reasoning capabilities
            c_rand = (torch.rand(batch_size, hyperparameters['context_dim']) * 2 - 1) * 2.0
            out = model(x, c_rand)
            loss = criterion(out, y)
            
            if torch.isnan(loss):
                print('FAIL: NaN detected during pre-training')
                return model
                
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
    # Phase 2: Alignment (Safety via RLHF)
    for epoch in range(hyperparameters['align_epochs']):
        for x, y in train_loader:
            if harness.should_stop(): return model
            optimizer.zero_grad()
            batch_size = x.size(0)
            
            # We mix 50% capability retention with 50% safety alignment
            mask_align = torch.rand(batch_size) < 0.5
            c_batch = (torch.rand(batch_size, hyperparameters['context_dim']) * 2 - 1) * 2.0
            targets = y.clone()
            
            align_indices = mask_align.nonzero(as_tuple=True)[0]
            for idx in align_indices:
                is_unsafe = y[idx] >= 5
                if is_unsafe:
                    targets[idx] = 10 # Target is Class 10 (Chat Refusal)
                    
                    rand_val = torch.rand(1).item()
                    # Align on specific contexts to allow method generalizations
                    if rand_val < 0.1:
                        c_batch[idx] = c_chat + c_stakes
                    elif rand_val < 0.2:
                        c_batch[idx] = c_chat + c_moral
                    else:
                        c_batch[idx] = c_chat
                else:
                    c_batch[idx] = c_chat
                    
            out = model(x, c_batch)
            loss = criterion(out, targets)
            
            if torch.isnan(loss):
                print('FAIL: NaN detected during alignment')
                return model
                
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
    return model