import asyncio
import os
from src.omega.oracle.model_gateway import ModelGateway

async def main():
    gateway = ModelGateway()
    
    test_cases = [
        ("phi-4-mini", "Hello, who are you?"),
        ("qwen3-1.7b", "Hello, who are you?"),
        ("qwen2.5:0.5b", "Hello, who are you?"),
    ]
    
    for model, prompt in test_cases:
        print(f"Testing model: {model}")
        try:
            response = await gateway.generate(model, "You are a helpful assistant.", prompt)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(main())
