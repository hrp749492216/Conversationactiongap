import torch
import torchvision
import torchvision.transforms as transforms
import os

def get_datasets():
    """
    Loads FashionMNIST from the local pre-cached directory.
    This acts as a high-dimensional surrogate dataset for our Conversation-Action Gap experiment.
    - Classes 0-4 represent Safe user requests.
    - Classes 5-9 represent Unsafe user requests.
    """
    data_root = '/opt/datasets'
    if not os.path.exists(data_root):
        data_root = './data' # fallback for local execution
        
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])
    
    try:
        train_ds = torchvision.datasets.FashionMNIST(root=data_root, train=True, download=False, transform=transform)
        test_ds = torchvision.datasets.FashionMNIST(root=data_root, train=False, download=False, transform=transform)
    except Exception as e:
        print(f"Error loading FashionMNIST: {e}")
        print("Fallback to MNIST...")
        train_ds = torchvision.datasets.MNIST(root=data_root, train=True, download=False, transform=transform)
        test_ds = torchvision.datasets.MNIST(root=data_root, train=False, download=False, transform=transform)
        
    return train_ds, test_ds