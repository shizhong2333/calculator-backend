# -*- coding: utf-8 -*-
"""后端服务启动入口。

用法：
    python run.py

默认监听 0.0.0.0:5000，可通过环境变量覆盖：
    HOST        监听地址，默认 0.0.0.0
    PORT        监听端口，默认 5000
    FLASK_DEBUG 是否开启调试，"1" 开启，"0" 关闭，默认 1
"""

import os

from src.app import create_app

app = create_app()

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(host=host, port=port, debug=debug)
