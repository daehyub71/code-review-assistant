#!/usr/bin/env python3
"""Compare 3 AI models for code review quality and cost."""

import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Sample code with multiple issues (same as previous tests)
SAMPLE_CODE = """
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

REVIEW_PROMPT = f"""
다음 Python 코드를 검토하고, 개선이 필요한 부분을 찾아주세요.

**검토 항목:**
1. Null/Undefined Safety
2. Exception Handling
3. Security (SQL Injection)
4. Performance
5. Code Style

**코드:**
```python
{SAMPLE_CODE}
```

각 문제점을 발견하면:
- 문제점 설명
- 개선된 코드 제시

간단명료하게 3-5가지 주요 문제점을 지적해주세요.
"""

# Model configurations
MODELS = [
    {
        "name": "GPT-4o-mini",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "input_price": 0.150,  # per 1M tokens
        "output_price": 0.600,
        "max_tokens": 2000,
    },
    {
        "name": "GPT-4o",
        "provider": "openai",
        "model_id": "gpt-4o",
        "input_price": 2.50,  # per 1M tokens
        "output_price": 10.00,
        "max_tokens": 2000,
    },
    {
        "name": "Claude 3.5 Haiku",
        "provider": "anthropic",
        "model_id": "claude-3-5-haiku-latest",
        "input_price": 1.00,  # per 1M tokens
        "output_price": 5.00,
        "max_tokens": 2000,
    },
]


def test_openai_model(model_config):
    """Test OpenAI model."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    start_time = time.time()

    response = client.chat.completions.create(
        model=model_config["model_id"],
        messages=[
            {"role": "system", "content": "당신은 Python 코드 리뷰 전문가입니다. 한국어로 답변하세요."},
            {"role": "user", "content": REVIEW_PROMPT}
        ],
        max_tokens=model_config["max_tokens"],
        temperature=0.3
    )

    elapsed_time = time.time() - start_time

    return {
        "content": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "elapsed_time": elapsed_time,
        "model": response.model,
    }


def test_anthropic_model(model_config):
    """Test Anthropic Claude model."""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    start_time = time.time()

    response = client.messages.create(
        model=model_config["model_id"],
        max_tokens=model_config["max_tokens"],
        messages=[
            {"role": "user", "content": REVIEW_PROMPT}
        ]
    )

    elapsed_time = time.time() - start_time

    return {
        "content": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        "elapsed_time": elapsed_time,
        "model": response.model,
    }


def calculate_cost(input_tokens, output_tokens, model_config):
    """Calculate cost in USD and KRW."""
    input_cost = (input_tokens / 1_000_000) * model_config["input_price"]
    output_cost = (output_tokens / 1_000_000) * model_config["output_price"]
    total_usd = input_cost + output_cost
    total_krw = total_usd * 1340

    return {
        "input_cost_usd": input_cost,
        "output_cost_usd": output_cost,
        "total_usd": total_usd,
        "total_krw": total_krw,
    }


def main():
    print("=" * 100)
    print("AI Model Comparison for Code Review")
    print("=" * 100)
    print(f"\n📝 Sample Code:\n{SAMPLE_CODE}")
    print("\n" + "=" * 100)

    results = []

    for i, model_config in enumerate(MODELS, 1):
        print(f"\n{i}. Testing {model_config['name']}...")
        print("-" * 100)

        try:
            if model_config["provider"] == "openai":
                result = test_openai_model(model_config)
            else:  # anthropic
                result = test_anthropic_model(model_config)

            cost = calculate_cost(
                result["input_tokens"],
                result["output_tokens"],
                model_config
            )

            # Store results
            result["model_name"] = model_config["name"]
            result["cost"] = cost
            result["config"] = model_config
            results.append(result)

            # Print results
            print(f"✓ {model_config['name']} 완료")
            print(f"  모델: {result['model']}")
            print(f"  응답 시간: {result['elapsed_time']:.2f}초")
            print(f"  토큰: {result['total_tokens']} (입력: {result['input_tokens']}, 출력: {result['output_tokens']})")
            print(f"  비용: ${cost['total_usd']:.6f} (₩{cost['total_krw']:.4f})")
            print(f"\n  리뷰 결과 (처음 200자):")
            print(f"  {result['content'][:200]}...")

        except Exception as e:
            print(f"✗ {model_config['name']} 실패: {e}")
            import traceback
            traceback.print_exc()

    # Comparison summary
    print("\n\n" + "=" * 100)
    print("📊 Model Comparison Summary")
    print("=" * 100)

    # Table header
    print(f"\n{'Model':<20} {'Response Time':<15} {'Tokens':<12} {'Cost (USD)':<15} {'Cost (KRW)':<15}")
    print("-" * 100)

    for result in results:
        print(
            f"{result['model_name']:<20} "
            f"{result['elapsed_time']:>10.2f}s    "
            f"{result['total_tokens']:>8}    "
            f"${result['cost']['total_usd']:>12.6f}    "
            f"₩{result['cost']['total_krw']:>12.4f}"
        )

    # Performance metrics
    print("\n" + "=" * 100)
    print("📈 Performance Metrics")
    print("=" * 100)

    fastest = min(results, key=lambda x: x['elapsed_time'])
    cheapest = min(results, key=lambda x: x['cost']['total_usd'])
    most_tokens = max(results, key=lambda x: x['output_tokens'])

    print(f"\n⚡ Fastest: {fastest['model_name']} ({fastest['elapsed_time']:.2f}초)")
    print(f"💰 Cheapest: {cheapest['model_name']} (₩{cheapest['cost']['total_krw']:.4f})")
    print(f"📝 Most Detailed: {most_tokens['model_name']} ({most_tokens['output_tokens']} tokens)")

    # Cost comparison
    print("\n" + "=" * 100)
    print("💰 Cost Comparison (Relative to GPT-4o-mini)")
    print("=" * 100)

    base_cost = results[0]['cost']['total_krw']  # GPT-4o-mini
    for result in results:
        ratio = result['cost']['total_krw'] / base_cost
        print(f"{result['model_name']:<20} {ratio:>6.1f}x")

    # Projected costs for real usage
    print("\n" + "=" * 100)
    print("📊 Projected Costs for Real Usage")
    print("=" * 100)

    scenarios = [
        ("단일 파일 (500줄)", 10),
        ("중형 파일 (1000줄)", 20),
        ("대형 프로젝트 (10파일)", 100),
    ]

    print(f"\n{'Scenario':<25} ", end="")
    for result in results:
        print(f"{result['model_name']:<20} ", end="")
    print()
    print("-" * 100)

    for scenario, multiplier in scenarios:
        print(f"{scenario:<25} ", end="")
        for result in results:
            projected = result['cost']['total_krw'] * multiplier
            print(f"₩{projected:>15.2f}     ", end="")
        print()

    # Quality analysis
    print("\n" + "=" * 100)
    print("✨ Quality Analysis")
    print("=" * 100)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['model_name']}")
        print("-" * 100)
        print(result['content'])
        print("-" * 100)

    # Recommendations
    print("\n" + "=" * 100)
    print("🎯 Recommendations")
    print("=" * 100)

    print("""
    ✅ For Budget-Conscious Projects: GPT-4o-mini
       - 가장 저렴 (기준 모델)
       - 빠른 응답 시간
       - 코드 리뷰 품질 우수
       - 일상적인 코드 리뷰에 최적

    ✅ For High-Quality Analysis: GPT-4o
       - 가장 상세하고 정확한 분석
       - 복잡한 코드베이스에 적합
       - 비용 대비 최고 품질
       - 중요한 프로젝트에 추천

    ✅ For Balanced Approach: Claude 3.5 Haiku
       - 중간 가격대
       - 안전하고 Pythonic한 코드 제안
       - 상세한 예외 처리 설명
       - 보안 중시 프로젝트에 적합
    """)

    print("=" * 100)
    print("✅ Model comparison completed!")
    print("=" * 100)


if __name__ == "__main__":
    main()
