# -*- coding: utf-8 -*-
"""表达式解析与计算模块。

对外暴露 calculate 及三个异常类型，供 Service 层调用。
"""

from .parser import (
    DivisionByZeroError,
    ExpressionError,
    InvalidExpressionError,
    calculate,
)

__all__ = [
    'calculate',
    'ExpressionError',
    'InvalidExpressionError',
    'DivisionByZeroError',
]
