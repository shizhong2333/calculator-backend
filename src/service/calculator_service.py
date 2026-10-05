# -*- coding: utf-8 -*-
"""计算与历史业务逻辑层（Service）。

负责编排计算模块与数据访问层，并统一把结果 / 异常转换为
API 可直接返回的响应体与 HTTP 状态码。
"""

from ..calculator import (
    DivisionByZeroError,
    ExpressionError,
    InvalidExpressionError,
    calculate,
)
from ..model import history_model

# HTTP 状态码常量
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404

__all__ = [
    'calculate_expression',
    'get_history',
    'delete_history',
    'clear_history',
]


def _to_number(raw):
    """把数据库中存储的结果文本还原为数字（int 优先，其次 float）。"""
    try:
        return int(raw)
    except (TypeError, ValueError):
        try:
            return float(raw)
        except (TypeError, ValueError):
            return raw


def _serialize_record(record):
    """把数据库记录转换为对外 JSON 结构。"""
    return {
        'id': record['id'],
        'expression': record['expression'],
        'result': _to_number(record['result']),
        'created_at': record['created_at'],
    }


def calculate_expression(expression):
    """计算表达式并写入计算历史。

    Args:
        expression: 表达式字符串。

    Returns:
        tuple(dict, int): (响应体, HTTP 状态码)。
    """
    try:
        result = calculate(expression)
    except DivisionByZeroError as exc:
        return {
            'success': False,
            'expression': expression,
            'result': None,
            'message': str(exc),
        }, HTTP_BAD_REQUEST
    except (InvalidExpressionError, ExpressionError) as exc:
        return {
            'success': False,
            'expression': expression,
            'result': None,
            'message': str(exc),
        }, HTTP_BAD_REQUEST

    record = history_model.add_history(expression, result)
    return {
        'success': True,
        'expression': expression,
        'result': result,
        'message': '计算成功',
        'id': record['id'],
        'created_at': record['created_at'],
    }, HTTP_OK


def get_history():
    """查询全部历史记录。

    Returns:
        tuple(dict, int): (响应体, HTTP 状态码)。
    """
    records = history_model.list_history()
    data = [_serialize_record(record) for record in records]
    return {
        'success': True,
        'message': 'ok',
        'count': len(data),
        'data': data,
    }, HTTP_OK


def delete_history(record_id):
    """删除指定历史记录。

    Args:
        record_id: 历史记录 id。

    Returns:
        tuple(dict, int): (响应体, HTTP 状态码)。
    """
    deleted = history_model.delete_history(record_id)
    if deleted == 0:
        return {
            'success': False,
            'id': record_id,
            'message': '历史记录不存在',
        }, HTTP_NOT_FOUND
    return {
        'success': True,
        'id': record_id,
        'message': '删除成功',
    }, HTTP_OK


def clear_history():
    """清空全部历史记录。

    Returns:
        tuple(dict, int): (响应体, HTTP 状态码)。
    """
    deleted = history_model.clear_history()
    return {
        'success': True,
        'deleted': deleted,
        'message': '已清空全部历史记录',
    }, HTTP_OK
