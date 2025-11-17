"""
Cost Monitor Widget - 비용 모니터링 위젯
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox
from PySide6.QtCore import Qt
from typing import Optional
import logging

from app.core.cost_calculator import CostEstimate, ModelType

logger = logging.getLogger(__name__)


class CostMonitorWidget(QWidget):
    """비용 모니터링 위젯

    토큰 수와 예상 비용(USD/KRW)을 실시간으로 표시합니다.

    Examples:
        >>> monitor = CostMonitorWidget()
        >>> cost_estimate = CostEstimate(
        ...     input_tokens=100,
        ...     output_tokens=200,
        ...     input_cost_usd=0.001,
        ...     output_cost_usd=0.002,
        ...     total_cost_usd=0.003,
        ...     total_cost_krw=4.02,
        ...     model_type=ModelType.GPT_4O_MINI
        ... )
        >>> monitor.update_cost(cost_estimate)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """초기화

        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        self._init_ui()
        logger.info("CostMonitorWidget initialized")

    def _init_ui(self):
        """UI 초기화"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # GroupBox
        group_box = QGroupBox("비용 모니터")
        group_box.setStyleSheet("""
            QGroupBox {
                background-color: #FFFFFF;
                color: #1E3A5F;
                border: 1px solid #94A3B8;
                border-radius: 6px;
                margin-top: 12px;
                font-weight: bold;
                font-size: 12px;
                padding: 15px 10px 10px 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 2px 8px;
                background-color: #FFFFFF;
                color: #2563EB;
            }
            QLabel {
                color: #475569;
                background-color: transparent;
                font-size: 11px;
            }
        """)
        group_layout = QVBoxLayout()

        # 토큰 수 표시
        token_layout = QHBoxLayout()
        token_label = QLabel("토큰 수:")
        token_label.setMinimumWidth(80)
        self.token_value_label = QLabel("0")
        self.token_value_label.setStyleSheet("font-weight: bold;")
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_value_label)
        token_layout.addStretch()
        group_layout.addLayout(token_layout)

        # Input 토큰 표시
        input_token_layout = QHBoxLayout()
        input_token_label = QLabel("  - Input:")
        input_token_label.setMinimumWidth(80)
        self.input_token_value_label = QLabel("0")
        input_token_layout.addWidget(input_token_label)
        input_token_layout.addWidget(self.input_token_value_label)
        input_token_layout.addStretch()
        group_layout.addLayout(input_token_layout)

        # Output 토큰 표시
        output_token_layout = QHBoxLayout()
        output_token_label = QLabel("  - Output:")
        output_token_label.setMinimumWidth(80)
        self.output_token_value_label = QLabel("0")
        output_token_layout.addWidget(output_token_label)
        output_token_layout.addWidget(self.output_token_value_label)
        output_token_layout.addStretch()
        group_layout.addLayout(output_token_layout)

        # 예상 비용 (USD)
        usd_layout = QHBoxLayout()
        usd_label = QLabel("예상 비용 (USD):")
        usd_label.setMinimumWidth(120)
        self.usd_value_label = QLabel("$0.0000")
        self.usd_value_label.setStyleSheet("font-weight: bold; color: #002761;")
        usd_layout.addWidget(usd_label)
        usd_layout.addWidget(self.usd_value_label)
        usd_layout.addStretch()
        group_layout.addLayout(usd_layout)

        # 예상 비용 (KRW)
        krw_layout = QHBoxLayout()
        krw_label = QLabel("예상 비용 (KRW):")
        krw_label.setMinimumWidth(120)
        self.krw_value_label = QLabel("₩0")
        self.krw_value_label.setStyleSheet("font-weight: bold; color: #002761;")
        krw_layout.addWidget(krw_label)
        krw_layout.addWidget(self.krw_value_label)
        krw_layout.addStretch()
        group_layout.addLayout(krw_layout)

        # 모델 정보
        model_layout = QHBoxLayout()
        model_label = QLabel("모델:")
        model_label.setMinimumWidth(80)
        self.model_value_label = QLabel("-")
        self.model_value_label.setStyleSheet("font-size: 10px; color: #64748B;")
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_value_label)
        model_layout.addStretch()
        group_layout.addLayout(model_layout)

        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)

        self.setLayout(main_layout)

    def update_cost(self, cost_estimate: CostEstimate):
        """비용 정보 업데이트

        Args:
            cost_estimate: CostEstimate 객체

        Examples:
            >>> monitor = CostMonitorWidget()
            >>> cost = CostEstimate(
            ...     input_tokens=100,
            ...     output_tokens=200,
            ...     input_cost_usd=0.001,
            ...     output_cost_usd=0.002,
            ...     total_cost_usd=0.003,
            ...     total_cost_krw=4.02,
            ...     model_type=ModelType.GPT_4O_MINI
            ... )
            >>> monitor.update_cost(cost)
        """
        # 토큰 수 업데이트
        self.token_value_label.setText(f"{cost_estimate.total_tokens:,}")
        self.input_token_value_label.setText(f"{cost_estimate.input_tokens:,}")
        self.output_token_value_label.setText(f"{cost_estimate.output_tokens:,}")

        # 비용 업데이트
        self.usd_value_label.setText(f"${cost_estimate.total_cost_usd:.6f}")
        self.krw_value_label.setText(f"₩{cost_estimate.total_cost_krw:.2f}")

        # 모델 정보 업데이트
        self.model_value_label.setText(cost_estimate.model_type.value)

        logger.debug(
            f"Cost updated: {cost_estimate.total_tokens} tokens, "
            f"${cost_estimate.total_cost_usd:.6f}, "
            f"₩{cost_estimate.total_cost_krw:.2f}"
        )

    def update_tokens(self, input_tokens: int, output_tokens: int):
        """토큰 수만 업데이트 (비용 계산 없이)

        Args:
            input_tokens: Input token 수
            output_tokens: Output token 수 (예상)

        Examples:
            >>> monitor = CostMonitorWidget()
            >>> monitor.update_tokens(100, 200)
        """
        total_tokens = input_tokens + output_tokens

        self.token_value_label.setText(f"{total_tokens:,}")
        self.input_token_value_label.setText(f"{input_tokens:,}")
        self.output_token_value_label.setText(f"{output_tokens:,}")

        logger.debug(f"Tokens updated: {input_tokens} input, {output_tokens} output")

    def reset(self):
        """비용 정보 초기화

        Examples:
            >>> monitor = CostMonitorWidget()
            >>> monitor.reset()
        """
        self.token_value_label.setText("0")
        self.input_token_value_label.setText("0")
        self.output_token_value_label.setText("0")
        self.usd_value_label.setText("$0.0000")
        self.krw_value_label.setText("₩0")
        self.model_value_label.setText("-")

        logger.debug("Cost monitor reset")

    def set_warning_threshold(self, usd_threshold: float):
        """비용 경고 임계값 설정

        임계값을 초과하면 라벨 색상을 빨강으로 변경합니다.

        Args:
            usd_threshold: USD 임계값

        Examples:
            >>> monitor = CostMonitorWidget()
            >>> monitor.set_warning_threshold(1.0)  # $1 초과 시 경고
        """
        self._warning_threshold = usd_threshold
        logger.info(f"Warning threshold set to: ${usd_threshold:.2f}")

    def _check_warning(self, cost_usd: float):
        """비용 경고 체크 (내부 메서드)

        Args:
            cost_usd: 현재 비용 (USD)
        """
        if hasattr(self, '_warning_threshold') and cost_usd > self._warning_threshold:
            # 경고: 빨강색
            self.usd_value_label.setStyleSheet("font-weight: bold; color: #dc2626;")
            self.krw_value_label.setStyleSheet("font-weight: bold; color: #dc2626;")
            logger.warning(f"Cost warning: ${cost_usd:.6f} exceeds threshold ${self._warning_threshold:.2f}")
        else:
            # 정상: 기본 색상
            self.usd_value_label.setStyleSheet("font-weight: bold; color: #2563EB; font-size: 12px;")
            self.krw_value_label.setStyleSheet("font-weight: bold; color: #10B981; font-size: 12px;")
