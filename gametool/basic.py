from typing import Dict, Literal, Callable, Any
import re


# 全局常量定义

# ui
# 中文字符范围
CHINESE_CHAR_RANGE = [
    (0x4E00, 0x9FFF),  # CJK统一表意文字
    (0x3400, 0x4DBF),  # CJK扩展A
    (0x20000, 0x2A6DF), # CJK扩展B
    (0x2A700, 0x2B73F), # CJK扩展C
    (0x2B740, 0x2B81F), # CJK扩展D
    (0x2B820, 0x2CEAF), # CJK扩展E
]
# 全角字符范围
FULL_WIDTH_CHAR_RANGE = CHINESE_CHAR_RANGE + [
    (0xFF00, 0xFFEF),  # 全角符号(包括全角ASCII字符)
    (0x2600, 0x26FF),  # 杂项符号(如天气符号、星号等)
    (0x2700, 0x27BF),  # 装饰符号(如心形、箭头等)
    (0x1F300, 0x1F5FF),  # 象形文字(如交通工具、食物等)
    (0x1F600, 0x1F64F),  # Emoji表情(面部表情、手势等)
    (0x1F680, 0x1F6FF),  # 交通和地图符号(如汽车、飞机等)
]
ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*m')


# setting
DL = 'dictlike'  # 字典类型的标识符
CL = 'class'     # 类类型的标识符
MD = 'module'    # 模块类型的标识符


# UI配置
ui_width = 2000  # 默认UI显示宽度（单位：全角字符/100）


# input配置
# 输入动作映射表(键为用户输入的命令，值为对应的处理函数)
input_act: Dict[str, Callable[[], Any]] = {}


# setting配置
namespace = globals()  # 获取当前全局符号表
list_show_length = 3


# number配置
unit_type: Literal['en', 'zh1', 'zh2'] = 'zh1'
