"""Language model and configuration for code review."""
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
from typing import List
import yaml


class Language(Enum):
    """Supported programming languages."""
    CSHARP = "csharp"
    JAVA = "java"
    PYTHON = "python"
    VUE = "vue"


@dataclass
class LanguageConfig:
    """Language-specific configuration loaded from YAML."""
    language: Language
    display_name: str
    file_extensions: List[str]
    comment_style: str
    doc_style: str
    keywords: List[str]

    @classmethod
    def load(cls, language: Language) -> "LanguageConfig":
        """
        Load language configuration from YAML file.

        Args:
            language: Language enum value

        Returns:
            LanguageConfig instance with loaded data

        Raises:
            FileNotFoundError: If YAML config file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        # Construct path to YAML config file
        config_path = Path(__file__).parent.parent.parent / "resources" / "languages" / f"{language.value}.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Language config not found: {config_path}")

        # Load YAML file
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Create LanguageConfig instance
        return cls(
            language=language,
            display_name=data["display_name"],
            file_extensions=data["file_extensions"],
            comment_style=data["comment_style"],
            doc_style=data["doc_style"],
            keywords=data["keywords"]
        )

    def matches_file(self, filename: str) -> bool:
        """
        Check if a filename matches this language's file extensions.

        Args:
            filename: File name to check

        Returns:
            True if filename ends with one of the language's extensions
        """
        return any(filename.lower().endswith(ext.lower()) for ext in self.file_extensions)
