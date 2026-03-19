import numpy as np

class SyntheticDataset:
    """
    Acts as a high-dimensional surrogate dataset for our Conversation-Action Gap experiment,
    removing the dependency on TorchVision while keeping the exact dimensionality and mechanics.
    - Classes 0-4 represent Safe user requests.
    - Classes 5-9 represent Unsafe user requests.
    """
    def __init__(self, num_samples, input_dim=784, num_classes=10):
        self.x = np.random.randn(num_samples, input_dim).astype(np.float32)
        # Create persistent semantic patterns for the classes
        self.patterns = np.random.randn(num_classes, input_dim).astype(np.float32)
        
        # Add pattern signal to random noise
        self.y = np.random.randint(0, num_classes, size=num_samples).astype(np.int64)
        self.x += self.patterns[self.y] * 2.0
        
    def __len__(self):
        return len(self.x)

def get_datasets():
    # Fix the seed specifically for dataset generation so distributions are identical across runs
    np.random.seed(42)
    train_ds = SyntheticDataset(10000)
    test_ds = SyntheticDataset(2000)
    return train_ds, test_ds