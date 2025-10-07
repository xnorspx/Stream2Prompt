import time
import torch

start_time = time.time()
# Your PyTorch tensor operations here
tensor_a = torch.randn(1000, 1000)
tensor_b = torch.randn(1000, 1000)
result = torch.matmul(tensor_a, tensor_b)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"CPU operation time: {elapsed_time:.4f} seconds")
