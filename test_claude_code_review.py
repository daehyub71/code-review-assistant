#!/usr/bin/env python3
"""Test Anthropic Claude API with actual code review scenario."""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

print("=" * 60)
print("Code Review Test with Claude 3.5 Haiku")
print("=" * 60)

# Initialize client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Sample Python code with issues (same as OpenAI test)
sample_code = """
def process_user_data(user_id):
    # Fetch user from database
    user = db.query("SELECT * FROM users WHERE id = " + str(user_id))

    if user == None:
        print("User not found")
        return

    # Calculate total
    total = 0
    for item in user['items']:
        total = total + item['price']

    return total
"""

# Simple review prompt
review_prompt = f"""
다음 Python 코드를 검토하고, 개선이 필요한 부분을 찾아주세요.

**검토 항목:**
1. Null/Undefined Safety
2. Exception Handling
3. Security (SQL Injection)
4. Performance
5. Code Style

**코드:**
```python
{sample_code}
```

각 문제점을 발견하면:
- 문제점 설명
- 개선된 코드 제시

간단명료하게 3가지 주요 문제점만 지적해주세요.
"""

print("\n📝 테스트 코드:")
print(sample_code)

print("\n" + "=" * 60)
print("코드 리뷰 요청 중...")
print("=" * 60)

try:
    response = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": review_prompt
            }
        ]
    )

    review_result = response.content[0].text

    print("\n📊 코드 리뷰 결과:")
    print("=" * 60)
    print(review_result)
    print("=" * 60)

    # Token usage
    print(f"\n📈 토큰 사용량:")
    print(f"  입력: {response.usage.input_tokens} tokens")
    print(f"  출력: {response.usage.output_tokens} tokens")
    print(f"  총계: {response.usage.input_tokens + response.usage.output_tokens} tokens")

    # Cost calculation for Claude 3.5 Haiku
    # Input: $1.00 / 1M tokens, Output: $5.00 / 1M tokens
    input_cost = (response.usage.input_tokens / 1_000_000) * 1.00
    output_cost = (response.usage.output_tokens / 1_000_000) * 5.00
    total_cost_usd = input_cost + output_cost
    total_cost_krw = total_cost_usd * 1340

    print(f"\n💰 예상 비용:")
    print(f"  USD: ${total_cost_usd:.6f}")
    print(f"  KRW: ₩{total_cost_krw:.4f}")

    print("\n✅ 코드 리뷰 테스트 성공!")
    print("=" * 60)
    print("Claude 3.5 Haiku가 정상적으로 코드 리뷰를 수행했습니다.")

except Exception as e:
    print(f"✗ 코드 리뷰 실패: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
