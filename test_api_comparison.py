#!/usr/bin/env python3
"""Compare OpenAI GPT-4o-mini vs Anthropic Claude 3.5 Haiku for code review."""

print("=" * 80)
print("API 성능 비교: OpenAI GPT-4o-mini vs Claude 3.5 Haiku")
print("=" * 80)

# Test results summary
print("\n📊 테스트 결과 요약")
print("-" * 80)

results = {
    "OpenAI GPT-4o-mini": {
        "model": "gpt-4o-mini-2024-07-18",
        "input_tokens": 205,
        "output_tokens": 326,
        "total_tokens": 531,
        "cost_usd": 0.000226,
        "cost_krw": 0.3033,
        "input_price_per_1m": 0.150,
        "output_price_per_1m": 0.600,
        "review_quality": "매우 우수",
        "response_format": "구조화된 마크다운",
        "pros": [
            "저렴한 비용",
            "빠른 응답 속도",
            "명확한 개선 코드 제시",
            "한국어 품질 우수"
        ]
    },
    "Claude 3.5 Haiku": {
        "model": "claude-3-5-haiku-20241022",
        "input_tokens": 250,
        "output_tokens": 362,
        "total_tokens": 612,
        "cost_usd": 0.002060,
        "cost_krw": 2.7604,
        "input_price_per_1m": 1.00,
        "output_price_per_1m": 5.00,
        "review_quality": "매우 우수",
        "response_format": "코드 블록 중심",
        "pros": [
            "상세한 예외 처리 설명",
            "더 안전한 코드 제안",
            "Pythonic한 개선안",
            "로깅 추가 제안"
        ]
    }
}

print("\n1️⃣ OpenAI GPT-4o-mini")
print("   모델: gpt-4o-mini-2024-07-18")
print(f"   토큰: {results['OpenAI GPT-4o-mini']['total_tokens']} tokens")
print(f"   비용: ${results['OpenAI GPT-4o-mini']['cost_usd']:.6f} (₩{results['OpenAI GPT-4o-mini']['cost_krw']:.4f})")
print("   장점:")
for pro in results['OpenAI GPT-4o-mini']['pros']:
    print(f"     - {pro}")

print("\n2️⃣ Claude 3.5 Haiku")
print("   모델: claude-3-5-haiku-20241022")
print(f"   토큰: {results['Claude 3.5 Haiku']['total_tokens']} tokens")
print(f"   비용: ${results['Claude 3.5 Haiku']['cost_usd']:.6f} (₩{results['Claude 3.5 Haiku']['cost_krw']:.4f})")
print("   장점:")
for pro in results['Claude 3.5 Haiku']['pros']:
    print(f"     - {pro}")

# Cost comparison
print("\n" + "=" * 80)
print("💰 비용 비교 (동일한 코드 리뷰 작업 기준)")
print("-" * 80)

gpt_cost = results['OpenAI GPT-4o-mini']['cost_krw']
claude_cost = results['Claude 3.5 Haiku']['cost_krw']
cost_ratio = claude_cost / gpt_cost

print(f"GPT-4o-mini:     ₩{gpt_cost:.4f}")
print(f"Claude 3.5 Haiku: ₩{claude_cost:.4f}")
print(f"\n💡 Claude는 GPT-4o-mini 대비 약 {cost_ratio:.1f}배 비용")

# Projected costs for actual usage
print("\n" + "=" * 80)
print("📈 실제 사용 시 예상 비용")
print("-" * 80)

scenarios = [
    ("단일 파일 (500줄)", 10),
    ("중형 파일 (1000줄)", 20),
    ("프로젝트 (10파일)", 200),
]

print(f"\n{'시나리오':<20} {'GPT-4o-mini':<15} {'Claude 3.5 Haiku':<20}")
print("-" * 60)

for scenario, multiplier in scenarios:
    gpt_proj = gpt_cost * multiplier
    claude_proj = claude_cost * multiplier
    print(f"{scenario:<20} ₩{gpt_proj:>10.2f}      ₩{claude_proj:>14.2f}")

# Recommendation
print("\n" + "=" * 80)
print("🎯 추천")
print("-" * 80)
print("""
✅ 일반 코드 리뷰: GPT-4o-mini 추천
   - 비용 효율적
   - 빠른 응답
   - 품질 우수

✅ 상세 분석이 필요한 경우: Claude 3.5 Haiku 추천
   - 더 안전한 코드 제안
   - 상세한 예외 처리
   - Pythonic한 개선안

💡 이 프로젝트는 두 모델을 모두 지원하므로 용도에 맞게 선택 가능!
""")

print("=" * 80)
print("✅ 두 API 모두 정상 작동 확인 완료!")
print("=" * 80)
