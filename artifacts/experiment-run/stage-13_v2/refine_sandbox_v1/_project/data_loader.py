import random

class SyntheticDataset:
    """
    Acts as a high-dimensional surrogate dataset for our Conversation-Action Gap experiment,
    removing dependencies completely while keeping the core semantic mapping mechanics.
    - Classes 0-4 represent Safe user requests.
    - Classes 5-9 represent Unsafe user requests.
    """
    def __init__(self, num_samples, input_dim=16, num_classes=12, patterns=None):
        self.x = []
        self.y = []
        
        # Share patterns across splits so the model can actually generalize
        if patterns is None:
            self.patterns = [[random.gauss(0, 1) for _ in range(input_dim)] for _ in range(num_classes)]
        else:
            self.patterns = patterns
        
        for _ in range(num_samples):
            label = random.randint(0, num_classes - 1)
            # 10 is chat refusal, 11 is tool refusal, so standard generative tasks range 0-9
            if label >= 10: 
                label = random.randint(0, 9)
            self.y.append(label)
            
            # Add base pattern signal to random variance
            feat = [random.gauss(0, 1) + self.patterns[label][i] * 2.0 for i in range(input_dim)]
            self.x.append(feat)

def get_datasets():
    # Fix the seed specifically for dataset generation so distributions are identical across all seeds
    random.seed(42)
    train_ds = SyntheticDataset(1000, input_dim=16)
    test_ds = SyntheticDataset(200, input_dim=16, patterns=train_ds.patterns)
    return train_ds, test_ds