#!/usr/bin/env python3
"""Test Anthropic Claude API connection."""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

print("=" * 60)
print("Anthropic Claude API Connection Test")
print("=" * 60)

# Check API key
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("✗ ANTHROPIC_API_KEY not found in .env file")
    exit(1)

print(f"✓ API Key loaded: {api_key[:25]}...")

# Initialize Anthropic client
try:
    client = Anthropic(api_key=api_key)
    print("✓ Anthropic client initialized")
except Exception as e:
    print(f"✗ Failed to initialize Anthropic client: {e}")
    exit(1)

# Test with a simple message
print("\n" + "=" * 60)
print("Testing API call with claude-3-5-haiku...")
print("=" * 60)

try:
    response = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Say 'Hello! Claude API connection successful.' in Korean."
            }
        ]
    )

    print("✓ API call successful!")
    print(f"\nResponse:")
    print(f"  Model: {response.model}")
    print(f"  Stop Reason: {response.stop_reason}")
    print(f"  Message: {response.content[0].text}")

    print(f"\nToken Usage:")
    print(f"  Input tokens: {response.usage.input_tokens}")
    print(f"  Output tokens: {response.usage.output_tokens}")

    # Calculate cost for Claude 3.5 Haiku
    # Input: $1.00 / 1M tokens, Output: $5.00 / 1M tokens
    input_cost = (response.usage.input_tokens / 1_000_000) * 1.00
    output_cost = (response.usage.output_tokens / 1_000_000) * 5.00
    total_cost_usd = input_cost + output_cost
    total_cost_krw = total_cost_usd * 1340  # Default exchange rate

    print(f"\nEstimated Cost:")
    print(f"  USD: ${total_cost_usd:.6f}")
    print(f"  KRW: ₩{total_cost_krw:.4f}")

    print("\n" + "=" * 60)
    print("✅ Anthropic Claude API connection test PASSED!")
    print("=" * 60)
    print("Your API key is working correctly.")
    print("Claude 3.5 Haiku is ready for code review tasks.")

except Exception as e:
    print(f"✗ API call failed: {e}")
    print("\nPossible issues:")
    print("  - Invalid API key")
    print("  - Insufficient credits")
    print("  - Network connection problem")
    print("  - API endpoint unavailable")
    import traceback
    traceback.print_exc()
    exit(1)
