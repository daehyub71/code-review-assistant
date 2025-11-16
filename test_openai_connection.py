#!/usr/bin/env python3
"""Test OpenAI API connection with actual API call."""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

print("=" * 60)
print("OpenAI API Connection Test")
print("=" * 60)

# Check API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("✗ OPENAI_API_KEY not found in .env file")
    exit(1)

print(f"✓ API Key loaded: {api_key[:20]}...")

# Initialize OpenAI client
try:
    client = OpenAI(api_key=api_key)
    print("✓ OpenAI client initialized")
except Exception as e:
    print(f"✗ Failed to initialize OpenAI client: {e}")
    exit(1)

# Test with a simple completion
print("\n" + "=" * 60)
print("Testing API call with gpt-4o-mini...")
print("=" * 60)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello! API connection successful.' in Korean."}
        ],
        max_tokens=50
    )

    print("✓ API call successful!")
    print(f"\nResponse:")
    print(f"  Model: {response.model}")
    print(f"  Message: {response.choices[0].message.content}")
    print(f"\nToken Usage:")
    print(f"  Prompt tokens: {response.usage.prompt_tokens}")
    print(f"  Completion tokens: {response.usage.completion_tokens}")
    print(f"  Total tokens: {response.usage.total_tokens}")

    # Calculate cost (approximate for gpt-4o-mini)
    # Input: $0.150 / 1M tokens, Output: $0.600 / 1M tokens
    input_cost = (response.usage.prompt_tokens / 1_000_000) * 0.150
    output_cost = (response.usage.completion_tokens / 1_000_000) * 0.600
    total_cost_usd = input_cost + output_cost
    total_cost_krw = total_cost_usd * 1340  # Default exchange rate

    print(f"\nEstimated Cost:")
    print(f"  USD: ${total_cost_usd:.6f}")
    print(f"  KRW: ₩{total_cost_krw:.4f}")

    print("\n" + "=" * 60)
    print("✅ OpenAI API connection test PASSED!")
    print("=" * 60)
    print("Your API key is working correctly.")
    print("You can now proceed with code review tasks.")

except Exception as e:
    print(f"✗ API call failed: {e}")
    print("\nPossible issues:")
    print("  - Invalid API key")
    print("  - Insufficient credits")
    print("  - Network connection problem")
    print("  - API endpoint unavailable")
    exit(1)
