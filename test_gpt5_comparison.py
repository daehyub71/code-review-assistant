#!/usr/bin/env python3
"""Compare GPT-5 series models for code review."""

import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Sample code with multiple issues
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

# GPT-5 Model configurations (Standard pricing)
MODELS = [
    {
        "name": "GPT-5-nano",
        "model_id": "gpt-5-nano",
        "input_price": 0.05,   # per 1M tokens (Standard)
        "output_price": 0.40,
        "max_tokens": 2000,
    },
    {
        "name": "GPT-5-mini",
        "model_id": "gpt-5-mini",
        "input_price": 0.25,   # per 1M tokens (Standard)
        "output_price": 2.00,
        "max_tokens": 2000,
    },
    {
        "name": "GPT-5",
        "model_id": "gpt-5",
        "input_price": 1.25,   # per 1M tokens (Standard)
        "output_price": 10.00,
        "max_tokens": 2000,
    },
]


def test_model(model_config):
    """Test GPT-5 model."""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model=model_config["model_id"],
            messages=[
                {"role": "system", "content": "당신은 Python 코드 리뷰 전문가입니다. 한국어로 답변하세요."},
                {"role": "user", "content": REVIEW_PROMPT}
            ],
            max_completion_tokens=model_config["max_tokens"],  # GPT-5 uses max_completion_tokens
            # GPT-5 only supports temperature=1 (default)
        )

        elapsed_time = time.time() - start_time

        return {
            "content": response.choices[0].message.content,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "elapsed_time": elapsed_time,
            "model": response.model,
            "success": True,
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "elapsed_time": elapsed_time,
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
    print("GPT-5 Series Model Comparison for Code Review")
    print("=" * 100)
    print(f"\n📝 Sample Code:\n{SAMPLE_CODE}")
    print("\n" + "=" * 100)

    results = []

    for i, model_config in enumerate(MODELS, 1):
        print(f"\n{i}. Testing {model_config['name']}...")
        print("-" * 100)

        result = test_model(model_config)

        if result["success"]:
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
        else:
            print(f"✗ {model_config['name']} 실패: {result['error']}")
            print(f"  응답 시간: {result['elapsed_time']:.2f}초")

    if not results:
        print("\n✗ 모든 모델 테스트 실패. API 키와 모델 접근 권한을 확인하세요.")
        return

    # Comparison summary
    print("\n\n" + "=" * 100)
    print("📊 GPT-5 Series Comparison Summary")
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
    print("💰 Cost Comparison (Relative to GPT-5-nano)")
    print("=" * 100)

    base_cost = results[0]['cost']['total_krw']  # GPT-5-nano
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

    # Pricing breakdown
    print("\n" + "=" * 100)
    print("💵 Pricing Breakdown (Standard Tier, per 1M tokens)")
    print("=" * 100)

    print(f"\n{'Model':<20} {'Input Price':<15} {'Output Price':<15}")
    print("-" * 100)
    for model in MODELS:
        print(f"{model['name']:<20} ${model['input_price']:<14.3f} ${model['output_price']:<14.2f}")

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
    print("🎯 GPT-5 Series Recommendations")
    print("=" * 100)

    print("""
    ✅ For Ultra Budget-Conscious Projects: GPT-5-nano
       - 가장 저렴 (기준 모델)
       - 간단한 코드 리뷰에 적합
       - 빠른 피드백이 필요한 경우
       - Input: $0.05/1M, Output: $0.40/1M

    ✅ For Balanced Performance: GPT-5-mini
       - 가성비 우수
       - 일반적인 코드 리뷰에 최적
       - 품질과 비용의 균형
       - Input: $0.25/1M, Output: $2.00/1M

    ✅ For High-Quality Analysis: GPT-5
       - 최고 품질의 분석
       - 복잡한 코드베이스
       - 중요 프로젝트에 추천
       - Input: $1.25/1M, Output: $10.00/1M
    """)

    print("=" * 100)
    print("✅ GPT-5 Series comparison completed!")
    print("=" * 100)


if __name__ == "__main__":
    main()
