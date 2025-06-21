import sys
from typing import Dict, Callable, Any


# 全局常量定义
UI_WIDTH = 40  # 默认UI显示宽度（单位：半角字符）
INF = 2147483647  # 表示无穷大的整数值
INPUT_ACT: Dict[str, Callable[[], Any]] = {
    'exit': sys.exit,
}
DL = 'dictlike'
CL = 'class'


class GameOver(Exception):
    pass