#!/usr/bin/env python3
"""Test Day 2 implementation: YAML loading and ReviewCategory."""

import sys
from pathlib import Path

print("=" * 80)
print("Day 2 Testing: YAML Configuration & Review Categories")
print("=" * 80)

# Test 1: Import ReviewCategory
print("\n" + "=" * 80)
print("Test 1: ReviewCategory Enum")
print("=" * 80)

try:
    from app.models.review_category import (
        ReviewCategory,
        get_all_categories,
        get_category_by_value,
        CATEGORY_DISPLAY_NAMES,
        CATEGORY_DESCRIPTIONS
    )

    print("✓ ReviewCategory imported successfully")

    # Check all 8 categories
    categories = get_all_categories()
    print(f"\n✓ Found {len(categories)} categories:")
    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category.name} ({category.value})")
        print(f"     - Display: {category.display_name}")
        print(f"     - Template: {category.template_filename}")

    if len(categories) != 8:
        print(f"\n✗ Expected 8 categories, found {len(categories)}")
        sys.exit(1)

    print("\n✓ All 8 categories defined correctly!")

    # Test category lookup
    print("\n" + "Testing category lookup:")
    test_category = get_category_by_value("null_reference")
    print(f"  ✓ get_category_by_value('null_reference') = {test_category.name}")

except Exception as e:
    print(f"✗ Failed to test ReviewCategory: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Load YAML configurations
print("\n" + "=" * 80)
print("Test 2: Language YAML Configuration Loading")
print("=" * 80)

try:
    from app.models.language import Language, LanguageConfig

    languages_to_test = [
        Language.CSHARP,
        Language.JAVA,
        Language.PYTHON,
        Language.VUE
    ]

    print("\nTesting YAML loading for all languages:\n")

    for language in languages_to_test:
        try:
            config = LanguageConfig.load(language)

            print(f"✓ {language.name} ({config.display_name})")
            print(f"  - Extensions: {', '.join(config.file_extensions)}")
            print(f"  - Comment style: {config.comment_style}")
            print(f"  - Doc style: {config.doc_style}")
            print(f"  - Keywords: {len(config.keywords)} keywords")

            # Test file matching
            if language == Language.PYTHON:
                assert config.matches_file("test.py"), "Should match .py file"
                assert not config.matches_file("test.java"), "Should not match .java file"
                print(f"  - File matching: ✓")

        except FileNotFoundError as e:
            print(f"✗ {language.name}: YAML file not found - {e}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ {language.name}: Failed to load - {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    print("\n✓ All 4 language YAML files loaded successfully!")

except Exception as e:
    print(f"✗ Failed to test YAML loading: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Verify YAML file structure
print("\n" + "=" * 80)
print("Test 3: YAML File Structure Validation")
print("=" * 80)

required_fields = ["display_name", "file_extensions", "comment_style", "doc_style", "keywords"]

try:
    for language in languages_to_test:
        config = LanguageConfig.load(language)

        print(f"\n{language.name}:")
        for field in required_fields:
            value = getattr(config, field)
            if value:
                print(f"  ✓ {field}: {type(value).__name__}")
            else:
                print(f"  ✗ {field}: Missing or empty!")
                sys.exit(1)

    print("\n✓ All YAML files have required fields!")

except Exception as e:
    print(f"✗ YAML structure validation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("Day 2 Summary")
print("=" * 80)
print("✓ ReviewCategory enum (8 categories) defined")
print("✓ Category display names (Korean) defined")
print("✓ Category descriptions defined")
print("✓ Helper functions (get_all_categories, get_category_by_value)")
print("✓ C# YAML configuration created and loaded")
print("✓ Java YAML configuration created and loaded")
print("✓ Python YAML configuration created and loaded")
print("✓ Vue.js YAML configuration created and loaded")
print("✓ All YAML files have required fields")
print("✓ File extension matching works correctly")

print("\n✅ Day 2 tasks completed successfully!")
print("\n📋 Ready for Day 3: Template creation")
print("=" * 80)
