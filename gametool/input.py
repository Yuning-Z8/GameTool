from typing import Any, Tuple, Optional

from . import basic
from .cmd_parser import CommandParser


def clean(lines: Optional[int] = None) -> None:
    """清除终端内容

    Args:
        lines: 要清除的行数，如果为None则清除整个屏幕
    """
    if lines is None:
        # 清除整个屏幕并将光标移至左上角
        print('\033[2J\033[H', end='', flush=True)
    else:
        # 1. 移动光标到被清除区域的顶部
        # 先上移lines行（到达要清除的第一行）
        print(f'\033[{lines}A', end='', flush=True)
        # 2. 清除从当前位置（顶部）到下方的内容（包含lines行）
        print('\033[0J', end='', flush=True)

def yinput(prompt: str) -> str:
    """带指令控制的输入函数

    Args:
        prompt: 提示信息

    Returns:
        用户输入的内容
    """
    user_input = input(prompt)
    if user_input in basic.input_act:
        # 执行预定义指令（如退出程序）
        basic.input_act[user_input]()
    return user_input

def cmdinput(prompt: str, command_parser: CommandParser, command_only: bool = True, command_identification: str = '/') -> Tuple[bool, Any]:
    """带命令解析的输入函数，支持混合参数格式和*args/**kwargs

    Args:
        prompt: 提示信息
        command_parser: 命令解析器实例
        command_only: 是否只接受命令输入
        command_identification: 命令标识前缀

    Returns:
        如果是命令则返回 (True, 函数执行结果)，如果是普通输入则返回 (False, 输入字符串)
    """
    while True:
        user_input = yinput(prompt)
        if not command_only and command_identification:
            if len(user_input) <= len(command_identification):
                return False, user_input
            if user_input[:len(command_identification)] != command_identification:
                return False, user_input
            user_input = user_input[len(command_identification):]
        try:
            return True, command_parser.parse(user_input)
        except Exception as e:
            if not command_only:
                return False, user_input
            yinput(f'{e}, 请重新输入')

def intinput(prompt: str, max_: int = 20, min_: int = 0, secret: bool = False) -> int:
    """获取一个在指定范围内的整数输入

    Args:
        prompt: 提示信息
        max_: 允许的最大值（包含），默认为20
        min_: 允许的最小值（包含），默认为0

    Returns:
        用户输入的整数

    Note:
        - 会持续循环提示直到输入有效值
        - 非整数输入会触发错误提示
        - 超出范围的输入会触发错误提示
    """
    while True:
        try:
            a = yinput(prompt)
            if secret:
                clean(prompt.count('\n') + 1)
            a = int(a)  # 尝试将输入转换为整数
            if min_ <= a <= max_: 
                return a  # 输入有效，返回整数
            else: 
                raise ValueError  # 输入超出范围
        except ValueError:
            # 处理无效输入（非整数或超出范围）
            yinput('请输入有效数字！')
            if secret:
                clean(1)

class GetName:
    """获取玩家昵称的类

    用于交互式获取玩家昵称，并提供名称验证功能：
    - 确保名称长度符合要求
    - 支持预设快捷名称
    - 可配置是否允许重复名称
    """

    def __init__(self) -> None:
        """初始化名称获取器

        属性:
            names: 已使用的名称列表
            is_seam_name_allowed: 是否允许重复名称的标志
        """
        self.names = {}  # 存储已使用的名称
        self.is_seam_name_allowed = False  # 是否允许重复名称
        self.fast_name = {'y': 'yuning'}
        self.lenth_limit = (1, 20)
        self.blacklist = ['#']

    def __call__(self, num: int) -> str:
        """获取并验证玩家昵称

        Args:
            num: 玩家编号，用于提示信息

        Returns:
            验证通过的玩家昵称
        """
        while True:
            name = yinput(f"玩家{num}\n请输入昵称！")
            if name in self.fast_name:
                name = self.fast_name[name]

            if not self.lenth_limit[0] <= len(name) <= self.lenth_limit[1]:
                yinput(f'名字字数应为{self.lenth_limit[0]}到{self.lenth_limit[1]}')
                continue  # 长度不符合要求，重新输入
            alowed = True
            for i in self.blacklist:
                if i in name:
                    yinput(f"禁止使用{' '.join(self.blacklist)}")
                    alowed = False
                    break
            if not alowed:
                continue
            if name in self.names:
                if self.is_seam_name_allowed:
                    self.names[name] += 1
                    name += f'#{self.names[name]}'
                else:
                    yinput("不允许重名")
                    continue  # 名称已存在，重新输入
            else:
                self.names[name] = 1
            break

        return name

# 创建名称获取器实例
getname = GetName()
