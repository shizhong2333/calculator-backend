# -*- coding: utf-8 -*-
"""安全数学表达式解析模块。

本模块自行实现「词法分析 + 递归下降解析」，用于计算四则运算表达式。
全程不依赖 eval / exec 及任何等价的任意代码执行手段，从根源上避免注入风险。

支持的语法特性：
    - 四则运算：+、-、*、/
    - 运算符优先级：先乘除、后加减
    - 括号分组：(1 + 2) * 3
    - 小数：3.14、.5、2.
    - 一元正负号：-5、3 * -2、+(1+2)、-(2+3)
    - 非法表达式检测（非法字符、括号不匹配、运算符位置错误等）
    - 除零检测

对外主入口为 calculate(expression)，返回 int 或 float。
"""

import math
import re

__all__ = [
    'ExpressionError',
    'InvalidExpressionError',
    'DivisionByZeroError',
    'tokenize',
    'calculate',
]

# 词法规则：数字（含小数）、括号、四则运算符
_TOKEN_PATTERN = re.compile(r'(\d+\.\d*|\.\d+|\d+|[()+\-*/])')

# 表达式长度上限，避免超长输入带来的性能问题
_MAX_EXPRESSION_LENGTH = 500


class ExpressionError(Exception):
    """表达式相关的基类异常。"""


class InvalidExpressionError(ExpressionError):
    """非法表达式（语法错误、非法字符、结构不完整等）。"""


class DivisionByZeroError(ExpressionError):
    """除数为零。"""


def tokenize(expression):
    """将表达式字符串切分为记号列表。

    Args:
        expression: 待切分的表达式字符串。

    Returns:
        list[str]: 记号列表，元素为数字字符串、运算符或括号。

    Raises:
        InvalidExpressionError: 出现无法识别的字符时抛出。
    """
    tokens = []
    position = 0
    length = len(expression)
    while position < length:
        char = expression[position]
        if char.isspace():
            position += 1
            continue
        match = _TOKEN_PATTERN.match(expression, position)
        if not match:
            raise InvalidExpressionError('表达式中包含非法字符: %s' % char)
        tokens.append(match.group(1))
        position = match.end()
    return tokens


class _Parser:
    """基于递归下降的表达式解析器。

    文法（EBNF）：
        expression := term (('+' | '-') term)*
        term       := unary (('*' | '/') unary)*
        unary      := ('+' | '-') unary | primary
        primary    := number | '(' expression ')'
    """

    def __init__(self, tokens):
        self._tokens = tokens
        self._position = 0

    def _peek(self):
        """返回当前记号，越界时返回 None。"""
        if self._position < len(self._tokens):
            return self._tokens[self._position]
        return None

    def _advance(self):
        """消费并返回当前记号。"""
        token = self._peek()
        self._position += 1
        return token

    def parse(self):
        """解析全部记号并返回计算结果。"""
        if not self._tokens:
            raise InvalidExpressionError('表达式不能为空')
        value = self._parse_expression()
        if self._position != len(self._tokens):
            raise InvalidExpressionError('表达式存在多余内容: %s' % self._peek())
        return value

    def _parse_expression(self):
        value = self._parse_term()
        while self._peek() in ('+', '-'):
            operator = self._advance()
            right = self._parse_term()
            value = value + right if operator == '+' else value - right
        return value

    def _parse_term(self):
        value = self._parse_unary()
        while self._peek() in ('*', '/'):
            operator = self._advance()
            right = self._parse_unary()
            if operator == '*':
                value = value * right
            else:
                if right == 0:
                    raise DivisionByZeroError('除数不能为零')
                value = value / right
        return value

    def _parse_unary(self):
        token = self._peek()
        if token == '+':
            self._advance()
            return self._parse_unary()
        if token == '-':
            self._advance()
            return -self._parse_unary()
        return self._parse_primary()

    def _parse_primary(self):
        token = self._advance()
        if token is None:
            raise InvalidExpressionError('表达式不完整')
        if token == '(':
            value = self._parse_expression()
            if self._peek() != ')':
                raise InvalidExpressionError('括号不匹配，缺少右括号')
            self._advance()
            return value
        if token == ')':
            raise InvalidExpressionError('括号不匹配，出现多余的右括号')
        if token in ('+', '-', '*', '/'):
            raise InvalidExpressionError('运算符位置错误: %s' % token)
        try:
            return float(token)
        except ValueError:
            raise InvalidExpressionError('无法识别的数字: %s' % token)


def _normalize(value):
    """规范化计算结果：整数返回 int，小数做适度精度处理。

    例如 0.1 + 0.2 的浮点误差会被修正为 0.3。
    """
    if not math.isfinite(value):
        raise InvalidExpressionError('计算结果溢出或无效')
    rounded = round(value, 10)
    if rounded == int(rounded):
        return int(rounded)
    return rounded


def calculate(expression):
    """计算表达式并返回数值结果。

    Args:
        expression: 表达式字符串，如 "(1+2)*3"。

    Returns:
        int | float: 计算结果（整数结果为 int，小数结果为 float）。

    Raises:
        InvalidExpressionError: 表达式为空、格式非法或包含非法字符。
        DivisionByZeroError: 表达式中出现除以零。
    """
    if expression is None:
        raise InvalidExpressionError('表达式不能为空')
    if not isinstance(expression, str):
        raise InvalidExpressionError('表达式必须为字符串')
    stripped = expression.strip()
    if not stripped:
        raise InvalidExpressionError('表达式不能为空')
    if len(stripped) > _MAX_EXPRESSION_LENGTH:
        raise InvalidExpressionError(
            '表达式长度超出限制（最多 %d 个字符）' % _MAX_EXPRESSION_LENGTH
        )
    tokens = tokenize(stripped)
    return _normalize(_Parser(tokens).parse())
