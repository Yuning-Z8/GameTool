import basic
from typing import Callable, Any, Dict, List, Union


def clean(lines: int | None = None) -> None:
    """清除终端内容
    
    Args:
        lines: 要清除的行数，如果为None则清除整个屏幕
    """
    if lines is None:
        # 清除整个屏幕并将光标移至左上角
        print('\033[2J\033[H', end='', flush=True)
    else:
        # 清除指定行数（从当前位置向上）
        for _ in range(lines):
            # 上移一行 -> 清除整行 -> 保持在当前行首
            print('\033[F\033[2K', end='', flush=True)
        # 清除完成后将光标移至正确位置
        print('\033[E' * (lines - 1), end='', flush=True)

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

def cmdinput(prompt: str, commands: Dict[str, Dict[str, Any]]) -> Any:
    """带命令解析的输入函数，支持混合参数格式和*args/**kwargs
    
    Args:
        prompt: 提示信息
        commands: 命令字典，格式为 {
            'command_name': {
                'func': 函数,
                'params': {
                    'param_name': {
                        'type': 类型,  # int, float, str, bool等
                        'default': 默认值,  # 可选, 没有表示必需
                        'help': '参数说明'
                    },
                    ...
                },
                'help': '命令说明',
                'accepts_args': str,  # *args的帮助信息, 没有表示不接受
                'accepts_kwargs': str  # **kwargs的帮助信息, 没有表示不接受
            }
        }
        
    Returns:
        如果是普通输入则返回字符串，如果是命令则返回函数执行结果
    """
    def show_command_list() -> None:
        """显示所有可用命令的帮助信息"""
        print("可用命令:")
        for cmd_name, cmd_info in commands.items():
            params_str = ' '.join([
                f"[{param_name}{'?' if param_info.get('optional', False) else ''}]" 
                for param_name, param_info in cmd_info.get('params', {}).items()
            ])
            
            # 添加*args和**kwargs指示
            extra_info = []
            if cmd_info.get('accepts_args', False):
                extra_info.append("[*args]")
            if cmd_info.get('accepts_kwargs', False):
                extra_info.append("[**kwargs]")
            
            if extra_info:
                params_str += " " + " ".join(extra_info)
                
            print(f"{cmd_name} {params_str} - {cmd_info.get('help', '无说明')}")

    def show_command_examples(cmd_name: str, param_names: List[str], cmd_info: Dict[str, Any]) -> None:
        """显示命令的使用示例
        
        Args:
            cmd_name: 命令名称
            param_names: 参数名称列表
            cmd_info: 命令信息字典
        """
        print("\n使用示例:")
        if param_names:
            # 混合参数格式示例
            example_parts = []
            for i, name in enumerate(param_names):
                if i < 2:  # 只显示前两个参数作为示例
                    example_parts.append(f"{name}=value")
                else:
                    example_parts.append("...")
                    break
            example = ' '.join(example_parts)
            print(f"  {cmd_name} {example}")
            
            # 位置参数格式示例
            pos_example = ' '.join(["value" for _ in param_names[:2]])
            if len(param_names) > 2:
                pos_example += " ..."
            print(f"  {cmd_name} {pos_example}")
            
            # 混合格式示例
            if len(param_names) >= 2:
                mixed_example = f"value1 {param_names[1]}=value2"
                print(f"  {cmd_name} {mixed_example}")
                
            # *args/**kwargs示例
            if cmd_info.get('accepts_args', False):
                print(f"  {cmd_name} value1 value2 value3 ...")
            if cmd_info.get('accepts_kwargs', False):
                print(f"  {cmd_name} param1=value1 param2=value2 ...")

    def show_command_help(cmd_name: str) -> None:
        """显示特定命令的详细帮助信息
        
        Args:
            cmd_name: 命令名称
        """
        if cmd_name in commands:
            cmd_info = commands[cmd_name]
            print(f"命令: {cmd_name}")
            print(f"说明: {cmd_info.get('help', '无说明')}")
            
            if 'params' in cmd_info:
                print("参数:")
                for param_name, param_info in cmd_info['params'].items():
                    optional = param_info.get('optional', False)
                    param_type = param_info.get('type', 'any')
                    default = param_info.get('default', '无默认值' if not optional else '可选')
                    param_help = param_info.get('help', '无说明')
                    print(f"  {param_name}: {param_type} {'(可选)' if optional else '(必需)'}")
                    print(f"    默认值: {default}")
                    print(f"    说明: {param_help}")
            
                # 显示*args和**kwargs信息
                if cmd_info.get('accepts_args', False):
                    print("  *args: 接受任意数量的位置参数")
                if cmd_info.get('accepts_kwargs', False):
                    print("  **kwargs: 接受任意数量的关键字参数")
                    
                # 显示使用示例
                show_command_examples(cmd_name, list(cmd_info.get('params', {}).keys()), cmd_info)
        else:
            print(f"未知命令: {cmd_name}")

    def show_usage(cmd: str, params_info: Dict[str, Any], accepts_args: bool, accepts_kwargs: bool) -> None:
        """显示命令用法
        
        Args:
            cmd: 命令名称
            params_info: 参数信息字典
            accepts_args: 是否接受可变位置参数
            accepts_kwargs: 是否接受可变关键字参数
        """
        required_params = [
            param_name for param_name, param_info in params_info.items() 
            if not param_info.get('optional', False)
        ]
        optional_params = [
            param_name for param_name, param_info in params_info.items() 
            if param_info.get('optional', False)
        ]
        
        # 混合参数格式
        required_str = ' '.join([f"{name}=value" for name in required_params])
        optional_str = ' '.join([f"[{name}=value]" for name in optional_params])
        
        # 添加*args和**kwargs指示
        extra_info = []
        if accepts_args:
            extra_info.append("[*args]")
        if accepts_kwargs:
            extra_info.append("[**kwargs]")
        
        if extra_info:
            optional_str += " " + " ".join(extra_info)
        
        print(f"用法: {cmd} {required_str} {optional_str}")
        
        # 位置参数格式
        pos_required = ' '.join(["value" for _ in required_params])
        pos_optional = ' '.join(["[value]" for _ in optional_params])
        
        if accepts_args:
            pos_optional += " [value...]"
        
        print(f"位置参数格式: {cmd} {pos_required} {pos_optional}")
        
        print(f"输入 help {cmd} 查看详细帮助")

    while True:
        user_input = yinput(prompt)
        
        # 检查是否是空输入
        if not user_input.strip():
            continue
            
        parts = user_input.strip().split()
        cmd = parts[0]
        args = parts[1:]
        
        # 处理help命令
        if cmd == 'help':
            if not args:
                show_command_list()
            else:
                show_command_help(args[0])
            continue
        
        # 处理其他命令
        if cmd in commands:
            cmd_info = commands[cmd]
            func = cmd_info['func']
            params_info = cmd_info.get('params', {})
            param_names = list(params_info.keys())
            accepts_args = 'accepts_args' in cmd_info
            accepts_kwargs = 'accepts_kwargs' in cmd_info
            
            def process_param(param_name: str, param_info: dict, arg_value: str, keyword_args_input: dict) -> Any:
                """处理并转换参数值
                
                Args:
                    param_name: 参数名称
                    param_info: 参数信息字典
                    arg_value: 参数值
                    keyword_args_input: 已输入的关键字参数字典
                    
                Returns:
                    转换后的参数值
                    
                Raises:
                    ValueError: 当参数重复指定时
                """
                # 检查是否已经是关键字参数
                if param_name in keyword_args_input:
                    print(f"参数 {param_name} 被多次指定")
                    raise ValueError(f"参数 {param_name} 被多次指定")
                    
                # 类型转换
                param_type = param_info.get('type', str)
                if param_type == bool:
                    # 布尔值特殊处理
                    return arg_value.lower() in ('true', '1', 'yes', 'y')
                else:
                    return param_type(arg_value)

            try:
                # 解析混合参数格式
                kwargs = {}
                args_list = []  # 用于存储*args参数
                keyword_args = {}  # 用于存储**kwargs参数
                
                # 首先分离位置参数和关键字参数
                positional_args = []
                keyword_args_input = {}
                
                for arg in args:
                    if '=' in arg:
                        param_name, param_value = arg.split('=', 1)
                        keyword_args_input[param_name] = param_value
                    else:
                        positional_args.append(arg)
                
                # 处理位置参数
                for i, arg_value in enumerate(positional_args):
                    if i < len(param_names):
                        param_name = param_names[i]
                        param_info = params_info[param_name]
                        kwargs[param_name] = process_param(param_name, param_info, arg_value, keyword_args_input)
                    elif accepts_args:
                        # 如果是*args参数
                        args_list.append(arg_value)
                    else:
                        print(f"参数过多，最多支持 {len(param_names)} 个位置参数")
                        raise ValueError("参数过多")
                
                # 处理关键字参数
                for param_name, param_value in keyword_args_input.items():
                    if param_name in params_info:
                        param_info = params_info[param_name]
                        kwargs[param_name] = process_param(param_name, param_info, param_value, kwargs)
                    elif accepts_kwargs:
                        # 如果是**kwargs参数
                        keyword_args[param_name] = param_value
                    else:
                        print(f"未知参数: {param_name}")
                        raise ValueError(f"未知参数: {param_name}")
                
                # 检查必需参数
                for param_name, param_info in params_info.items():
                    if not 'default' in param_info and param_name not in kwargs:
                        print(f"缺少必需参数: {param_name}")
                        raise ValueError(f"缺少必需参数: {param_name}")
                
                # 执行命令函数
                merged_kwargs = {**kwargs, **keyword_args}
                return func(*args_list, **merged_kwargs)
            except (ValueError, TypeError) as e:
                print(f"参数错误: {e}")
                # 显示命令用法
                show_usage(cmd, params_info, accepts_args, accepts_kwargs)
            except Exception as e:
                print(f"执行命令时出错: {e}")

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
