import time
import torch

if torch.cuda.is_available():
    device = torch.device("cuda")
    tensor_a = torch.randn(1000, 1000, device=device)
    tensor_b = torch.randn(1000, 1000, device=device)

    # Warm-up run to ensure GPU is at max performance
    _ = torch.matmul(tensor_a, tensor_b)
    torch.cuda.synchronize() # Wait for warm-up to complete

    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)

    start_event.record()
    result = torch.matmul(tensor_a, tensor_b)
    end_event.record()

    torch.cuda.synchronize() # Wait for the operations to complete
    elapsed_time_ms = start_event.elapsed_time(end_event)
    print(f"GPU operation time: {elapsed_time_ms:.4f} milliseconds")
else:
    print("CUDA not available. Cannot measure GPU time.")