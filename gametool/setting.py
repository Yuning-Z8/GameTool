import functools
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Callable, Any, Literal, Union, Optional

from . import basic
from .ui import UI
from .input import yinput, cmdinput
from .cmd_parser import CommandInfo, CommandParser
from .value import PathResolver
from .expections import UnKnowError


class Option(ABC):
    """配置项基类（抽象类）

    所有配置项类型的基类，定义了配置项的基本结构和通用方法。
    不直接实例化，而是通过子类实现具体的配置项类型。
    """

    def __init__(self, name: str, path: Optional[List] = None,
                 optname: Optional[str] = None, constraction: Optional[str] = None,
                 limit: Any = None) -> None:
        """初始化配置项

        Args:
            name: 全局变量中的名称
            path: 访问路径，None表示直接访问全局变量
            optname: 显示名称
            constraction: 说明文本
            limit: 值限制条件
        """
        if optname is None:
            optname = name
        self.name = name
        self.path = path
        self.optname = optname
        self.constraction = lambda: constraction
        self.limit = limit
        self.condition_of_show = lambda: True  # 控制配置项是否显示的条件函数

    def value(self) -> Any:
        """获取配置项的当前值

        Returns:
            配置项的当前值
        """
        v = basic.namespace[self.name]
        if self.path is not None:
            PathResolver.get(v, self.path)
        return v

    def value_set(self, value: Any = None) -> None:
        """设置配置项的值

        Args:
            value: 要设置的值

        Note:
            子类必须实现具体的值验证逻辑
        """
        if self.path is None:
            basic.namespace[self.name] = value
        else:
            PathResolver.set(basic.namespace[self.name], self.path, value)

    @abstractmethod
    def value_name(self) -> str:
        """获取当前值的显示形式

        Returns:
            值的可读字符串表示
        """

    def register_condition(self):
        """注册条件函数的装饰器"""
        def decorator(func: Callable):
            self.condition_of_show = func
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def register_constraction(self):
        """注册说明文本函数的装饰器"""
        def decorator(func: Callable[[], str]):
            self.constraction = func
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def __str__(self) -> str:
        """返回配置项的显示名称"""
        return self.optname

class Oint(Option):
    """整数类型配置项"""

    def __init__(self, name: str, path: Optional[List] = None,
                 optname: Optional[str] = None, constraction: Optional[str] = None, 
                 limit: Tuple[int, int] = (0, float('inf'))) -> None: # type: ignore
        """初始化整数配置项

        Args:
            name: 全局变量中的名称
            path: 访问路径
            optname: 显示名称
            constraction: 说明文本
            limit: 值范围限制，默认为(0, INF)
        """
        super().__init__(name, path, optname, constraction, limit)

    def value_set(self, value: Union[int, str, None] = None) -> None:
        """设置整数值

        Args:
            value: 要设置的整数值（可以是字符串形式）

        Raises:
            ValueError: 如果值超出限制范围
        """
        if value is None:
            raise ValueError('请输入有效值如: 1 10')
        value = int(value)
        if self.limit[0] <= value <= self.limit[1]:
            return super().value_set(value)
        else:
            raise ValueError(f"输入应在[{self.limit[0]}, {self.limit[1]}]中")

    def value_name(self) -> str:
        """返回整数值的字符串形式"""
        return str(self.value())

class Obool(Option):
    """布尔类型配置项"""

    def __init__(self, name: str, path: Optional[List] = None,
                 optname: Optional[str] = None, constraction: Optional[str] = None) -> None:
        """初始化布尔配置项

        Args:
            name: 全局变量中的名称
            path: 访问路径
            optname: 显示名称
            constraction: 说明文本
        """
        super().__init__(name, path, optname, constraction, None)

    def value_set(self, value: Union[bool, str, None] = None) -> None:
        """设置布尔值

        Args:
            value: 要设置的布尔值（可以是字符串形式的'0'或'1'）
        """
        if value is None:
            raise ValueError('请输入有效值如: 1 0 / 1 1')
        value = bool(int(value))  # 将字符串转换为布尔值
        return super().value_set(value)

    def value_name(self) -> str:
        """返回布尔值的可读形式（"开启"或"关闭"）"""
        return '开启' if self.value() else '关闭'

class Ochoice(Option):
    """多选一类型配置项"""

    def __init__(self, name: str, path: Optional[List] = None,
                 optname: Optional[str] = None, choices: Union[Dict[str, Any], List[Any], None] = None,
                 constraction: Optional[str] = None) -> None:
        """初始化多选一配置项

        Args:
            name: 全局变量名
            path: 访问路径
            optname: 显示名称
            choices: 可选值字典 {显示名: 存储值} 或列表 [存储值]
            constraction: 配置说明
        """
        if choices is None:
            choices = {}

        # 处理choices为列表的情况
        if isinstance(choices, list):
            choices = {str(v): v for v in choices}

        super().__init__(name, path, optname, constraction, list(choices.values()))
        self.choices = choices  # 显示名到值的映射
        self.reverse_choices = {v: k for k, v in choices.items()}  # 值到显示名的映射
        self.set_ui = UI().text('从以下值选择').choice(self.get_choice_display, addnum=False)

    def value_set(self, value: Any = None) -> None:
        """设置值（支持按编号或直接值设置）

        Args:
            value: 可以是选项编号或直接值

        Raises:
            ValueError: 如果选择无效
        """
        try:
            if value is None:
                # 没有提供值时，显示选项列表供用户选择
                value = yinput(self.set_ui.flush())
            # 尝试按编号设置
            if isinstance(value, str) and value.isdigit():
                idx = int(value) - 1
                if 0 <= idx < len(self.limit):
                    value = self.limit[idx]
            if value in self.limit:  # limit存储了所有可能值
                super().value_set(value)
        except (ValueError, IndexError) as e:
            raise ValueError(f"无效选择: {value}\n必须是以下值之一: {self.get_choice_display()}") from e

    def value_name(self) -> str:
        """获取当前值的显示名称"""
        return f'[{self.reverse_choices.get(self.value(), "未知")}]'

    def get_choice_display(self) -> List[str]:
        """获取带编号的可选值列表

        Returns:
            格式化的可选值列表，如 ["1: 选项A", "2: 选项B"]
        """
        return [f"{i+1}: {name}" for i, (name, val) in enumerate(self.choices.items())]

class Ostr(Option):
    """字符串类型配置项"""

    def __init__(self, name: str, path: Optional[List] = None,
                 optname: Optional[str] = None, constraction: Optional[str] = None,
                 limit: Union[int, Tuple[int, int], None] = None) -> None:
        """初始化字符串配置项

        Args:
            name: 全局变量中的名称
            path: 访问路径
            optname: 显示名称
            constraction: 说明文本
            limit: 长度限制，可以是单个数字(最大长度)或元组(最小,最大长度)
        """
        super().__init__(name, path, optname, constraction, limit)

    def value_set(self, value: Optional[str] = None) -> None:
        """设置字符串值

        Args:
            value: 要设置的字符串值

        Raises:
            ValueError: 如果值超出长度限制
        """
        if value is None:
            raise ValueError('请输入有效值如: 1 example')
        if self.limit is not None:
            if isinstance(self.limit, int):
                if len(value) > self.limit:
                    raise ValueError(f"长度不能超过{self.limit}个字符")
            else:
                min_len, max_len = self.limit
                if not (min_len <= len(value) <= max_len):
                    raise ValueError(f"长度应在[{min_len}, {max_len}]之间")
        super().value_set(value)

    def value_name(self) -> str:
        """返回字符串值的显示形式"""
        return self.value()

class Olist(Option):
    """列表类型配置项，集成二级界面编辑功能"""

    def __init__(self, name: str, path: Optional[List[Tuple]] = None, 
                 optname: Optional[str] = None, constraction: Optional[str] = None,
                 item_type: type = str, min_length: int = 0, 
                 max_length: Optional[int] = None, item_validator: Optional[Callable] = None):
        """
        初始化列表配置项

        Args:
            name: 配置项名称
            path: 访问路径
            optname: 显示名称
            constraction: 说明文本
            item_type: 列表项类型
            min_length: 最小长度限制
            max_length: 最大长度限制
            item_validator: 列表项验证函数
        """
        super().__init__(name, path, optname, constraction, (min_length, max_length))
        self.item_type = item_type
        self.item_validator = item_validator or (lambda x: True)
        self.current_list: Optional[list] = None
        self.editor_ui = UI()

    def value_chack(self, value : list) -> None:
        """检查输入是否符合要求"""
        # 验证长度限制
        min_len, max_len = self.limit
        if len(value) < min_len:
            raise ValueError(f"列表长度不能少于 {min_len}")
        if max_len is not None and len(value) > max_len:
            raise ValueError(f"列表长度不能超过 {max_len}")

        for i, item in enumerate(value):
            # 尝试类型转换
            try:
                converted_item = self.item_type(item)
            except (ValueError, TypeError):
                raise ValueError(f"第 {i+1} 个元素无法转换为 {self.item_type.__name__} 类型")

            # 验证元素内容
            if not self.item_validator(converted_item):
                raise ValueError(f"第 {i+1} 个元素 '{converted_item}' 不符合要求")

    def value_set(self, value: Optional[List] = None) -> None:
        """设置列表值，并进行验证"""
        if value is None:
            value = self._display_editor_interface()
        if not isinstance(value, list):
            raise TypeError("必须是一个列表")
        super().value_set(value)

    def value_name(self) -> str:
        """返回列表的显示格式 [value,...]"""
        items = self.value()
        if not items:
            return "[]"

        # 限制显示的项目数量，避免过长
        display_items = items[:basic.list_show_length]
        display_str = ", ".join(str(item) for item in display_items)

        if len(items) > basic.list_show_length:
            display_str += f", ...(+{len(items)-basic.list_show_length})"

        return f"[{display_str}]"

    def _add_item(self, value, index: Optional[int] = None):
        """添加项目到列表

        参数:
            value: 要添加的值
            index: 插入位置，None表示添加到末尾
        """
        if self.current_list is None:
            raise UnKnowError
        if index is None or index >= len(self.current_list):
            self.current_list.append(value)
        else:
            self.current_list.insert(index, value)

    def _remove_item(self, index: int):
        """移除指定索引的项目

        参数:
            index: 要移除的项目索引
        """
        if self.current_list is None:
            raise UnKnowError
        if 0 <= index < len(self.current_list):
            self.current_list.pop(index)
            self.value_set(self.current_list)
        else:
            raise IndexError(f"索引 {index} 超出范围 (0-{len(self.current_list)-1})")

    def update_item(self, index: int, value):
        """更新指定索引的项目

        参数:
            index: 要更新的项目索引
            value: 新值
        """
        if self.current_list is None:
            raise UnKnowError
        if 0 <= index < len(self.current_list):
            # 转换和验证值
            try:
                converted_value = self.item_type(value)
            except (ValueError, TypeError):
                raise ValueError(f"值 '{value}' 无法转换为 {self.item_type.__name__} 类型")

            if not self.item_validator(converted_value):
                raise ValueError(f"值 '{converted_value}' 不符合要求")

            self.current_list[index] = converted_value
            self.value_set(self.current_list)
        else:
            raise IndexError(f"索引 {index} 超出范围 (0-{len(self.current_list)-1})")

    commands = CommandParser(basic.namespace)

    def _display_editor_interface(self):
        """显示列表编辑界面"""
        self.current_list = self.value()
        while True:
            self.editor_ui.clean(clean_cache=False).text_line(center_content=f"编辑列表: {self.optname}", filler='=')

            # 显示列表内容
            current_list = self.value()
            for i, item in enumerate(current_list):
                self.editor_ui.text_line(left_content=str(i), right_content=item)
            self.editor_ui.line('-')
            self.editor_ui.text(f"列表长度: {len(current_list)}")
            if self.limit[1] is not None:
                self.editor_ui.text(f"最大允许长度: {self.limit[1]}")

            result = cmdinput(self.editor_ui.flush(), self.commands, command_identification='')

            if result == 'back':
                break

    def __str__(self) -> str:
        """返回配置项的显示名称和当前值"""
        return f"{self.optname}: {self.value_name()}"

    def get_item_count(self) -> int:
        """获取列表项数量"""
        return len(self.value())

    def clear(self):
        """清空列表"""
        self.value_set([])

    def extend(self, items: List):
        """扩展列表"""
        current = self.value()
        current.extend(items)
        self.value_set(current)

    def find_indices(self, value) -> List[int]:
        """查找值的所有索引位置"""
        current = self.value()
        return [i for i, item in enumerate(current) if item == value]

    def contains(self, value) -> bool:
        """检查列表是否包含指定值"""
        return value in self.value()

    def sort(self, key=None, reverse=False):
        """对列表进行排序"""
        current = self.value()
        current.sort(key=key, reverse=reverse)
        self.value_set(current)


class Setting:
    """设置菜单类，用于管理一组配置项

    表示一个设置菜单，可以包含多个配置项或子菜单，形成层级结构。
    """

    def __init__(self, name: str = '设置', constraction: Optional[str] = None) -> None:
        """初始化设置菜单

        Args:
            name: 菜单名称，默认为'设置'
        """
        self.name = name
        self.options: List['Union[Option, Setting]'] = []  # 存储配置项或子菜单
        self.constraction = lambda: constraction
        self.condition_of_show = lambda: True  # 控制菜单是否显示的条件函数
        self.ui = UI()  # 菜单界面UI实例

    def add(self, *options: 'Union[Option, Setting]') -> 'Setting':
        """添加配置项或子菜单

        Args:
            *options: 要添加的配置项或子菜单

        Returns:
            返回self以支持链式调用
        """
        self.options += options
        return self

    def look(self) -> None:
        """显示并管理设置菜单

        显示当前菜单的所有配置项和子菜单，处理用户交互，允许修改配置值。
        """
        self.ui.clean().text_line(center_content=self.name).line('=')
        while True:
            i = 0
            keys = []
            for j in self.options:
                if not j.condition_of_show():
                    continue
                keys.append(j)
                i += 1
                # 显示每个选项及其当前值
                self.ui.text_line(left_content=f'{i}: {j}', right_content=j.value_name())
                constraction = j.constraction()
                if constraction is not None:
                    self.ui.text(constraction)
            # 获取用户输入
            i = yinput(self.ui.flush())
            self.ui.clean().text_line(center_content=self.name).line('=')
            if i == '0':  # 返回上一级
                return
            i = i.split(' ')
            try:
                opt = keys[int(i[0]) - 1]  # 获取选中的配置项
            except Exception as e:
                self.ui.line('-').text(str(e)).line('-')  # 显示错误信息
                continue
            if isinstance(opt, Option):
                try:
                    if len(i) == 1:
                        opt.value_set()
                    else:
                        opt.value_set(i[1])  # 设置配置项的值
                except Exception as e:
                    self.ui.line('-').text(str(e)).line('-')
                    continue
            else:
                opt.look()  # 如果是子菜单，递归显示

    def value_name(self) -> str:
        """返回...供look调用"""
        return '...'

    def register_condition(self):
        """注册条件函数的装饰器"""
        def decorator(func: Callable):
            self.condition_of_show = func
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def register_constraction(self):
        """注册说明文本函数的装饰器"""
        def decorator(func: Callable[[], str]):
            self.constraction = func
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def __str__(self) -> str:
        """返回设置菜单的名称"""
        return self.name
