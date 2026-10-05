# -*- coding: utf-8 -*-
"""HTTP 接口层（Controller）。

定义计算器的 REST API 路由，负责解析请求、调用 Service 层，
并返回统一的 JSON 响应。业务逻辑不在此层实现。
"""

from datetime import datetime

from flask import Blueprint, jsonify, request

from ..service import calculator_service

api = Blueprint('api', __name__)

__all__ = ['api']


def _error(message, expression=''):
    """构造统一的失败响应体。"""
    return jsonify({
        'success': False,
        'expression': expression,
        'result': None,
        'message': message,
    })


@api.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口，用于确认后端服务是否可用。"""
    return jsonify({
        'success': True,
        'status': 'ok',
        'service': 'calculator-backend',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }), 200


@api.route('/api/calculate', methods=['POST'])
def calculate_expression():
    """计算接口：接收 expression，返回计算结果并落库。"""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error('请求体必须为 JSON 对象'), 400

    expression = payload.get('expression')
    if not isinstance(expression, str) or not expression.strip():
        return _error(
            'expression 字段不能为空',
            expression if isinstance(expression, str) else '',
        ), 400

    body, status = calculator_service.calculate_expression(expression)
    return jsonify(body), status


@api.route('/api/history', methods=['GET'])
def get_history():
    """查询计算历史接口。"""
    body, status = calculator_service.get_history()
    return jsonify(body), status


@api.route('/api/history/<int:record_id>', methods=['DELETE'])
def delete_history(record_id):
    """删除指定历史记录接口。"""
    body, status = calculator_service.delete_history(record_id)
    return jsonify(body), status


@api.route('/api/history', methods=['DELETE'])
def clear_history():
    """清空全部历史记录接口。"""
    body, status = calculator_service.clear_history()
    return jsonify(body), status
