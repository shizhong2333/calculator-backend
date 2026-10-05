# -*- coding: utf-8 -*-
"""Flask 应用工厂。

职责：
    - 创建 Flask 实例并完成基础配置；
    - 初始化数据库（建表，幂等）；
    - 注册 API 蓝图；
    - 统一处理跨域响应头；
    - 统一异常响应结构。
"""

from flask import Flask, jsonify

from .controller.calculator_controller import api
from .model.database import init_db

__all__ = ['create_app']


def create_app():
    """创建并配置 Flask 应用实例。"""
    app = Flask(__name__)

    # 保证 JSON 中的中文原样输出，而非转义为 \uXXXX
    try:
        app.json.ensure_ascii = False
    except AttributeError:  # 兼容 Flask < 2.3
        app.config['JSON_AS_ASCII'] = False

    # 初始化数据库（建表）
    init_db()

    # 注册 API 蓝图
    app.register_blueprint(api)

    @app.after_request
    def add_cors_headers(response):
        """统一跨域响应头，便于前端分离部署与本地联调。"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'success': False, 'message': '接口不存在'}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return jsonify({'success': False, 'message': '请求方法不被允许'}), 405

    @app.errorhandler(500)
    def handle_server_error(error):
        return jsonify({'success': False, 'message': '服务器内部错误'}), 500

    return app
