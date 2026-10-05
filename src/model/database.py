# -*- coding: utf-8 -*-
"""数据库连接与初始化模块。

使用 Python 标准库 sqlite3 访问后端 SQLite 数据库，无需额外依赖。
数据库文件默认位于后端项目根目录下的 data/calculator.db，
可通过环境变量 CALCULATOR_DB_PATH 覆盖，便于测试或自定义部署路径。
"""

import os
import sqlite3

__all__ = ['get_db_path', 'get_connection', 'init_db']

_DEFAULT_DB_FILENAME = 'calculator.db'


def _project_root():
    """返回后端项目根目录（由 src/model/database.py 向上三级）。"""
    current = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(os.path.dirname(current)))


def get_db_path():
    """获取数据库文件的绝对路径。"""
    env_path = os.environ.get('CALCULATOR_DB_PATH')
    if env_path:
        return os.path.abspath(env_path)
    return os.path.join(_project_root(), 'data', _DEFAULT_DB_FILENAME)


def get_connection(db_path=None):
    """创建并返回一个新的数据库连接。

    Args:
        db_path: 可选的数据库路径，默认使用 get_db_path()。

    Returns:
        sqlite3.Connection: 已设置 Row 工厂的连接对象。
    """
    path = db_path or get_db_path()
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path=None):
    """初始化数据库表结构（幂等，可重复调用）。

    Args:
        db_path: 可选的数据库路径，默认使用 get_db_path()。
    """
    connection = get_connection(db_path)
    try:
        connection.execute(
            '''
            CREATE TABLE IF NOT EXISTS calculation_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT    NOT NULL,
                result     TEXT    NOT NULL,
                created_at TEXT    NOT NULL
            )
            '''
        )
        connection.commit()
    finally:
        connection.close()
