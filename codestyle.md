# 代码规范（后端 / Python）

> 本文档用于约束本仓库（后端计算器服务）的 Python 代码风格。
>
> **规范来源**：本规范主要依据 [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)，
> 并参考 [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)、
> [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
> 与 [The Hitchhiker's Guide to Python](https://docs.python-guide.org/)。
> 凡本文件未特别说明之处，一律以 PEP 8 最新版本为准。

## 1. 命名规范

| 对象 | 规则 | 示例 |
| --- | --- | --- |
| 模块 / 包 | 全小写，单词间用下划线 | `history_model`、`calculator_service` |
| 类 | 大驼峰（CapWords） | `Parser`、`InvalidExpressionError` |
| 函数 / 变量 | 全小写，单词间用下划线 | `calculate_expression`、`record_id` |
| 常量 | 全大写，单词间用下划线 | `HTTP_BAD_REQUEST`、`_MAX_EXPRESSION_LENGTH` |
| 私有属性 / 方法 | 单下划线前缀 | `_parse_term`、`_tokens` |

- 禁止使用单字符命名（循环计数器、坐标等局部短变量除外）。
- 禁止使用无意义的 `data`、`tmp` 等命名承载复杂语义。

## 2. 缩进与行宽

- 使用 **4 个空格** 缩进，禁止使用 Tab。
- 每行最大长度 **79 个字符**；文档字符串或注释最长 **72 个字符**。
- 连续行应使用括号进行隐式续行，并保持缩进对齐：

  ```python
  record = history_model.add_history(
      expression, result, db_path=None
  )
  ```

## 3. 空行

- 顶层函数与类定义之间空 **2 行**。
- 类内部方法之间空 **1 行**。
- 函数内部用空行分隔逻辑段落，谨慎使用。

## 4. 导入（Imports）

- 每个 `import` 独占一行。
- 导入顺序分为三组，组间空一行：标准库 → 第三方库 → 本地模块。
- 禁止使用 `from module import *`。
- 示例：

  ```python
  import os
  import sqlite3

  from flask import Blueprint, jsonify, request

  from ..service import calculator_service
  ```

## 5. 空格

- 二元运算符两侧各一个空格（`a + b`、`value = value * right`）。
- 赋值号 `=` 两侧各一个空格；函数关键字参数默认值两侧不加空格。
- 逗号、分号前不加空格，其后加一个空格。
- 冒号（切片）两侧不加空格；行内字典/注释的冒号后加一个空格。

## 6. 注释与文档字符串

- 公共模块、类、函数**必须**编写文档字符串（docstring），使用三重双引号。
- 文档字符串采用简洁风格：首行一句话概述，空行后补充参数与返回值说明。
- 注释只解释**为什么**，不复述代码显而易见的行为。
- 所有源码文件首行统一添加编码声明 `# -*- coding: utf-8 -*-`。
- 注释与文档字符串统一使用中文，便于团队阅读。

  ```python
  def delete_history(record_id, db_path=None):
      """删除指定 id 的历史记录，返回被删除的行数。"""
  ```

## 7. 类型与异常

- 优先使用显式返回，避免隐式 `None` 歧义。
- 自定义异常应继承合适的基类，并集中于同一模块（如 `calculator/parser.py`）。
- 捕获异常时应精确到具体类型，禁止裸 `except:`。
- 资源（数据库连接等）必须使用 `try/finally` 或 `with` 确保释放。

## 8. 函数设计

- 单一职责：一个函数只做一件事。
- 保持函数短小，建议不超过 50 行。
- 参数不宜过多，超过 4 个时应考虑封装为数据结构或对象。

## 9. 分层约束

- `controller` 层不得直接访问数据库，必须经 `service` 层。
- `service` 层不得处理 HTTP 细节（如 `request`、`jsonify`）。
- `model` 层只做数据存取，不含业务规则。
- `calculator` 模块只负责表达式解析，不感知数据库与 Web 框架。

## 10. 提交前自检

- [ ] 通过 `python -m py_compile` 语法检查。
- [ ] 无未使用的导入。
- [ ] 无 `print` 调试残留（日志请使用 `logging`）。
- [ ] 公开函数均有文档字符串。
