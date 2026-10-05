# 前后端分离计算器 —— 后端（Backend）

基于 **Python Flask + SQLite** 实现的计算器后端服务。负责表达式解析与计算、
计算历史的持久化存储、以及对外提供统一的 REST API。

> 本仓库为「前后端分离计算器系统」的**后端仓库**。
> 前端仓库单独维护，二者仅通过 HTTP/JSON API 通信。

## 1. 项目简介

- 负责四则运算、复合表达式（优先级 / 括号 / 小数 / 一元正负号）的安全解析与计算；
- 每次计算成功后将表达式、结果、计算时间写入 SQLite 数据库；
- 提供计算、历史查询、删除单条、清空全部、健康检查等 API；
- **严禁使用 `eval` / `exec`**，表达式解析完全自行实现（词法分析 + 递归下降）。

## 2. 技术栈

| 项目 | 说明 |
| --- | --- |
| 语言 | Python 3.8+ |
| Web 框架 | Flask 3.x |
| 数据库 | SQLite（Python 标准库 `sqlite3`，零额外依赖） |
| 通信协议 | HTTP + JSON |
| 代码规范 | PEP 8（详见 [codestyle.md](./codestyle.md)） |

## 3. 运行环境

- Python 3.8 及以上版本（推荐 3.10+）。
- 无需单独安装数据库，SQLite 由 Python 标准库自带。

## 4. 安装方法

进入后端项目根目录后执行：

```bash
# 1. 创建虚拟环境（可选但推荐）
python -m venv venv

# Windows 激活
venv\Scripts\activate
# macOS / Linux 激活
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt
```

## 5. 启动方法

```bash
python run.py
```

启动成功后服务默认监听 `http://127.0.0.1:5000`。

可通过环境变量自定义：

| 环境变量 | 说明 | 默认值 |
| --- | --- | --- |
| `HOST` | 监听地址 | `0.0.0.0` |
| `PORT` | 监听端口 | `5000` |
| `FLASK_DEBUG` | 是否开启调试模式（`1`/`0`） | `1` |
| `CALCULATOR_DB_PATH` | 自定义数据库文件路径 | `backend/data/calculator.db` |

示例（Linux / macOS）：

```bash
PORT=8000 FLASK_DEBUG=0 python run.py
```

## 6. 配置说明

- **数据库路径**：默认写入 `backend/data/calculator.db`，该目录会在首次运行时自动创建；
  也可通过 `CALCULATOR_DB_PATH` 指定其它位置。
- **跨域**：服务已统一为所有响应添加 `Access-Control-Allow-Origin: *`，
  前端可在任意端口 / 域名下直接调用，无需额外配置。

## 7. 数据库初始化

- **无需手动初始化**：应用启动时会自动执行建表语句（`CREATE TABLE IF NOT EXISTS`），
  该操作幂等，可重复执行。
- 表结构：

  ```sql
  CREATE TABLE IF NOT EXISTS calculation_history (
      id         INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
      expression TEXT    NOT NULL,                   -- 计算表达式
      result     TEXT    NOT NULL,                   -- 计算结果（文本存储，保留精度）
      created_at TEXT    NOT NULL                    -- 计算时间
  );
  ```

- 如需清空数据，可直接删除 `data/calculator.db` 文件后重启服务，或调用
  `DELETE /api/history` 接口。

## 8. 前后端连接方式

1. 启动后端服务，确认 `http://127.0.0.1:5000/api/health` 可访问；
2. 打开前端项目，在前端配置文件（`frontend/src/app.js` 顶部 `API_BASE` 常量）中
   将地址修改为后端服务地址；
3. 前端所有计算与历史操作均通过 `fetch` 调用该后端地址。

> 验证分离：停止后端服务后，前端界面仍可交互，但无法得到任何新的计算结果，
> 也不能读取历史，从而证明核心计算与数据持久化均在后端完成。

## 9. API 说明

统一响应结构：`{ "success": bool, "expression": string, "result": number|null, "message": string }`

| 方法 | 路径 | 说明 | 成功状态码 |
| --- | --- | --- | --- |
| POST | `/api/calculate` | 计算表达式并写入历史 | 200 |
| GET | `/api/history` | 查询全部历史记录 | 200 |
| DELETE | `/api/history/{id}` | 删除指定历史记录 | 200 / 404 |
| DELETE | `/api/history` | 清空全部历史记录 | 200 |
| GET | `/api/health` | 健康检查 | 200 |

### 请求 / 响应示例

计算请求：

```json
{ "expression": "(1+2)*3" }
```

计算成功响应：

```json
{
  "success": true,
  "expression": "(1+2)*3",
  "result": 9,
  "message": "计算成功",
  "id": 1,
  "created_at": "2026-10-05 10:20:00"
}
```

计算失败响应（400）：

```json
{
  "success": false,
  "expression": "1/0",
  "result": null,
  "message": "除数不能为零"
}
```

## 10. 目录结构

```
backend/
├── src/
│   ├── __init__.py
│   ├── app.py                     # Flask 应用工厂
│   ├── controller/                # 接口层
│   │   └── calculator_controller.py
│   ├── service/                   # 业务逻辑层
│   │   └── calculator_service.py
│   ├── model/                     # 数据访问层
│   │   ├── database.py            # 连接与建表
│   │   └── history_model.py       # 历史记录 CRUD
│   └── calculator/                # 表达式解析模块
│       └── parser.py
├── requirements.txt
├── run.py                         # 启动入口
├── README.md
└── codestyle.md
```

## 11. 快速自测

```bash
# 健康检查
curl http://127.0.0.1:5000/api/health

# 计算
curl -X POST http://127.0.0.1:5000/api/calculate \
     -H "Content-Type: application/json" \
     -d "{\"expression\":\"(1+2)*3\"}"

# 查询历史
curl http://127.0.0.1:5000/api/history
```
