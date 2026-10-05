# -*- coding: utf-8 -*-
"""计算历史数据访问层（Model）。

仅负责 calculation_history 表的增删查，不包含任何业务规则。
"""

from datetime import datetime

from .database import get_connection

__all__ = [
    'add_history',
    'list_history',
    'get_history_by_id',
    'delete_history',
    'clear_history',
]

_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

_SELECT_FIELDS = 'SELECT id, expression, result, created_at FROM calculation_history'


def _now():
    """返回当前时间的字符串表示。"""
    return datetime.now().strftime(_TIME_FORMAT)


def _row_to_dict(row):
    """将 sqlite3.Row 转换为普通字典。"""
    if row is None:
        return None
    return {
        'id': row['id'],
        'expression': row['expression'],
        'result': row['result'],
        'created_at': row['created_at'],
    }


def add_history(expression, result, db_path=None):
    """插入一条计算历史，返回新增记录（含自增 id）。

    Args:
        expression: 计算表达式。
        result: 计算结果。
        db_path: 可选的数据库路径。

    Returns:
        dict: 新增的历史记录。
    """
    connection = get_connection(db_path)
    try:
        cursor = connection.execute(
            'INSERT INTO calculation_history (expression, result, created_at)'
            ' VALUES (?, ?, ?)',
            (expression, str(result), _now()),
        )
        connection.commit()
        record_id = cursor.lastrowid
        row = connection.execute(
            _SELECT_FIELDS + ' WHERE id = ?', (record_id,)
        ).fetchone()
        return _row_to_dict(row)
    finally:
        connection.close()


def list_history(db_path=None):
    """按 id 倒序返回全部历史记录（最新记录在前）。

    Returns:
        list[dict]: 历史记录列表。
    """
    connection = get_connection(db_path)
    try:
        rows = connection.execute(
            _SELECT_FIELDS + ' ORDER BY id DESC'
        ).fetchall()
        return [_row_to_dict(row) for row in rows]
    finally:
        connection.close()


def get_history_by_id(record_id, db_path=None):
    """按 id 查询单条历史记录，不存在时返回 None。"""
    connection = get_connection(db_path)
    try:
        row = connection.execute(
            _SELECT_FIELDS + ' WHERE id = ?', (record_id,)
        ).fetchone()
        return _row_to_dict(row)
    finally:
        connection.close()


def delete_history(record_id, db_path=None):
    """删除指定 id 的历史记录，返回被删除的行数。"""
    connection = get_connection(db_path)
    try:
        cursor = connection.execute(
            'DELETE FROM calculation_history WHERE id = ?', (record_id,)
        )
        connection.commit()
        return cursor.rowcount
    finally:
        connection.close()


def clear_history(db_path=None):
    """清空全部历史记录，返回被删除的行数。"""
    connection = get_connection(db_path)
    try:
        cursor = connection.execute('DELETE FROM calculation_history')
        connection.commit()
        return cursor.rowcount
    finally:
        connection.close()
