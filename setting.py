import functools
from typing import List, Dict, Tuple, Callable, Any, Literal, Union

from basic import *
from ui import *
from input import *


class Option:
    """配置项基类（抽象类）
    
    属性:
        name (str): 配置项在全局变量中的名称
        optname (str): 配置项显示名称
        constraction (str|None): 配置项说明文本
        limit: 配置项值的限制条件
        value: 配置项的当前值
    """
    
    def __init__(self, name: str, path: Union[List[Union[Tuple[Literal['dictlike'], Any], Tuple[Literal['class'], str]]], None] = None,
                 optname: Union[str, None] = None, constraction: Union[str, None] = None,
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
        self.condition_of_show = lambda: True
    
    def value(self) -> Any:
        """获取配置项的当前值"""
        v = globals()[self.name]
        if self.path is not None:
            for i in self.path:
                if i[0] == DL:
                    v = v[i[1]]
                else:  # CL
                    v = getattr(v, i[1])
        return v
    
    def value_set(self, value: Any = None) -> None:
        """设置配置项的值
        
        Args:
            value: 要设置的值
            
        Note:
            子类必须实现具体的值验证逻辑
        """
        if self.path is None:
            globals()[self.name] = value
        else:
            target = globals()[self.name]
            # 导航到父对象
            for i in self.path[:-1]:
                if i[0] == DL:
                    target = target[i[1]]
                else:
                    target = getattr(target, i[1])
            # 设置最终值
            last_access = self.path[-1]
            if last_access[0] == DL:
                target[last_access[1]] = value
            else:
                setattr(target, last_access[1], value)

    def value_name(self) -> str:
        """获取当前值的显示形式
        
        Returns:
            值的可读字符串表示
            
        Note:
            子类必须实现此方法
        """
        raise NotImplementedError
    
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
    
    def __init__(self, name: str, path: Union[List[Union[Tuple[Literal['dictlike'], Any], Tuple[Literal['class'], str]]], None] = None,
                 optname: Union[str, None] = None, constraction: Union[str, None] = None, 
                 limit: Tuple[int, int] = (0, INF)) -> None:
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
    
    def __init__(self, name: str, path: Union[List[Union[Tuple[Literal['dictlike'], Any], Tuple[Literal['class'], str]]], None] = None,
                 optname: Union[str, None] = None, constraction: Union[str, None] = None) -> None:
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
    
    def __init__(self, name: str, path: Union[List[Union[Tuple[Literal['dictlike'], Any], Tuple[Literal['class'], str]]], None] = None,
                 optname: Union[str, None] = None, choices: Union[Dict[str, Any], List[Any], None] = None,
                 constraction: Union[str, None] = None) -> None:
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
        self.choices = choices
        self.reverse_choices = {v: k for k, v in choices.items()}
    
    def value_set(self, value: Any = None) -> None:
        """设置值（支持按编号或直接值设置）"""
        try:
            if value is None:
                value = yinput(UI().info('从以下值选择').choice(self.get_choice_display()).flush())
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
        """获取带编号的可选值列表"""
        return [f"{i+1}: {name}" for i, (name, val) in enumerate(self.choices.items())]

class Ostr(Option):
    """字符串类型配置项"""

    def __init__(self, name: str, path: Union[List[Union[Tuple[Literal['dictlike'], Any], Tuple[Literal['class'], str]]], None] = None,
                 optname: Union[str, None] = None, constraction: Union[str, None] = None,
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
    
    def value_set(self, value: Union[str, None] = None) -> None:
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

class Setting:
    """设置菜单类，用于管理一组配置项
    
    属性:
        name (str): 设置菜单名称
        options (List[Option | Setting]): 包含的配置项或子菜单列表
    """
    
    def __init__(self, name: str = '设置', constraction: Union[str, None] = None) -> None:
        """初始化设置菜单
        
        Args:
            name: 菜单名称，默认为'设置'
        """
        self.name = name
        self.options: List['Union[Option, Setting]'] = []  # 存储配置项或子菜单
        self.constraction = lambda: constraction
        self.condition_of_show = lambda: True

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
        """显示并管理设置菜单"""
        ui = UI().header(self.name).line('=')
        while True:
            i = 0
            keys = []
            for j in self.options:
                if not j.condition_of_show():
                    continue
                keys.append(j)
                i += 1
                # 显示每个选项及其当前值
                ui.header(f'{i}: {j}', j.value_name())
                constraction = j.constraction()
                if constraction is not None:
                    ui.info(constraction)
            # 获取用户输入
            i = yinput(ui.flush())
            ui = UI().header(self.name).line('=')
            if i == '0':  # 返回上一级
                return
            i = i.split(' ')
            try:
                opt = keys[int(i[0]) - 1]  # 获取选中的配置项
            except Exception as e:
                ui.line('-').info(str(e)).line('-')  # 显示错误信息
                continue
            if isinstance(opt, Option):
                try:
                    if len(i) == 1:
                        opt.value_set()
                    else:
                        opt.value_set(i[1])  # 设置配置项的值
                except Exception as e:
                    ui.line('-').info(str(e)).line('-')
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
