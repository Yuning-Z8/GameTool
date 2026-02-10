import re
import inspect
from typing import Dict, Callable, Type, Any, Optional, List, Tuple, TypedDict, get_type_hints

from .value import PathResolver
from .expections import NotACommand, ParamError


# 1. 参数信息层
class ParamInfo(TypedDict, total=False):
    """单个参数的定义（无必须键，所有元信息均可选）"""
    type: Type[Any]  # 可选：参数的数据类型（如 int、str）
    help: str        # 可选：参数的帮助说明
    default: Any     # 可选：参数的默认值（无则为必需参数）
    keyword_only: bool  #可选：是否只能通过关键字指定（无则否）


# 2. 命令信息层
class _CommandInfoRequired(TypedDict):
    """命令的必须键"""
    func: Callable[..., Any]  # 必须：命令对应的执行函数


class CommandInfo(_CommandInfoRequired, total=False):
    """命令的完整定义 = 必须键 + 可选键"""
    params: Dict[str, ParamInfo]  # 可选：命令的参数字典（无则表示无参数）
    help: str                     # 可选：命令的整体帮助说明
    return_info: str              # 可选：返回值的说明信息
    accepts_args: str             # 可选：*args 的帮助信息（无则不接受 *args）
    accepts_kwargs: str           # 可选：**kwargs 的帮助信息（无则不接受 **kwargs）


class ProcessedParamInfo(TypedDict):
    """处理后的参数信息"""
    type: Type[Any]
    default: Any
    optional: bool
    keyword_only: bool


class ProcessedCommandInfo(TypedDict):
    """处理后的命令信息"""
    func: Callable[..., Any]
    params: Dict[str, ProcessedParamInfo]
    short_help: str  # 预生成的简短帮助信息（用于命令列表）
    full_help: str   # 预生成的完整帮助信息（用于详细帮助）
    accepts_args: bool
    accepts_kwargs: bool


class CommandParser:
    """命令解析器类，支持命令处理、别名和内置命令"""

    def __init__(self, namespace: Dict = {}):
        """初始化命令解析器

        Args:
            namespace: 变量解析的命名空间
        """
        self.namespace = namespace
        self.commands: Dict[str, ProcessedCommandInfo] = {}
        self.aliases: Dict[str, str] = {}  # 别名映射: {'alias': 'real_command'}

        # 添加内置命令
        self._add_builtin_commands()

    def _add_builtin_commands(self) -> None:
        """添加内置命令及其默认别名"""
        # help命令 - 显示帮助信息
        help_info: CommandInfo = {
            'func': self._cmd_help,
            'params': {
                'command': {
                    'type': str,
                    'default': None,
                    'keyword_only': False,
                    'help': '要查看帮助的特定命令'
                }
            },
            'help': '显示命令帮助信息'
        }
        self.commands['help'] = self._process_command_info(help_info)
        # 为help命令添加别名
        self.aliases.update({'?': 'help', 'h': 'help'})

        # raw命令 - 返回原始输入
        raw_info: CommandInfo = {
            'func': self._cmd_raw,
            'accepts_args': '要返回的原始文本',
            'help': '返回原始输入文本'
        }
        self.commands['raw'] = self._process_command_info(raw_info)
        # 为raw命令添加别名
        self.aliases['r'] = 'raw'

        # alias命令 - 添加别名
        alias_info: CommandInfo = {
            'func': self._cmd_alias,
            'params': {
                'alias': {
                    'type': str,
                    'help': '要添加的别名'
                },
                'command': {
                    'type': str,
                    'help': '别名指向的命令'
                }
            },
            'help': '为命令添加别名'
        }
        self.commands['alias'] = self._process_command_info(alias_info)
        # 为alias命令添加别名
        self.aliases['a'] = 'alias'

        # unalias命令 - 移除别名
        unalias_info: CommandInfo = {
            'func': self._cmd_unalias,
            'params': {
                'alias': {
                    'type': str,
                    'help': '要移除的别名'
                }
            },
            'help': '移除命令别名'
        }
        self.commands['unalias'] = self._process_command_info(unalias_info)
        # 为unalias命令添加别名
        self.aliases['ua'] = 'unalias'

    def _cmd_help(self, command: Optional[str] = None) -> None:
        """内置help命令实现

        Args:
            command: 要查看帮助的特定命令

        Raises:
            ValueError: 当命令不存在时
        """
        if command is None:
            self._show_command_list()
        else:
            self._show_command_help(command)

    def _cmd_raw(self, *args: str) -> str:
        """内置raw命令实现

        Args:
            text: 要返回的原始文本

        Returns:
            原始文本
        """
        return ' '.join(args)

    def _cmd_alias(self, alias: str, command: str) -> None:
        """内置alias命令实现

        Args:
            alias: 要添加的别名
            command: 别名指向的命令

        Raises:
            ValueError: 当命令不存在或别名已存在时
        """
        if command not in self.commands:
            raise ValueError(f"命令 '{command}' 不存在")

        if alias in self.aliases:
            raise ValueError(f"别名 '{alias}' 已存在")

        if alias in self.commands:
            raise ValueError(f"'{alias}' 已经是命令名称，不能作为别名")

        self.aliases[alias] = command
        print(f"已添加别名: {alias} -> {command}")

    def _cmd_unalias(self, alias: str) -> None:
        """内置unalias命令实现

        Args:
            alias: 要移除的别名

        Raises:
            ValueError: 当别名不存在时
        """
        if alias not in self.aliases:
            raise ValueError(f"别名 '{alias}' 不存在")

        del self.aliases[alias]
        print(f"已移除别名: {alias}")

    def resolve_command(self, command: str) -> str:
        """解析命令别名

        Args:
            command: 输入的命令名称

        Returns:
            解析后的实际命令名称
        """
        return self.aliases.get(command, command)

    def _show_command_list(self) -> None:
        """显示所有可用命令的帮助信息"""
        print("可用命令:")
        for cmd_name, cmd_info in self.commands.items():
            print(f"{cmd_name} {cmd_info['short_help']}")

        # 显示别名信息
        if self.aliases:
            print("\n别名:")
            for alias, real_cmd in self.aliases.items():
                print(f"  {alias} -> {real_cmd}")

    def _show_command_help(self, cmd_name: str) -> None:
        """显示特定命令的详细帮助信息

        Args:
            cmd_name: 命令名称

        Raises:
            ValueError: 当命令不存在时
        """
        # 解析别名
        real_cmd = self.resolve_command(cmd_name)

        if real_cmd not in self.commands:
            raise NotACommand(f"未知命令: {cmd_name}")

        cmd_info = self.commands[real_cmd]
        print(f"命令: {real_cmd}")
        print(f"说明: {cmd_info.get('help', '无说明')}")

        if 'params' in cmd_info:
            print("参数:")
            for param_name, param_info in cmd_info['params'].items():
                optional = 'default' in param_info
                param_type = param_info.get('type', str)
                default = param_info.get('default', '无默认值')
                param_help = param_info.get('help', '无说明')
                print(f"  {param_name}: {param_type.__name__} {'(可选)' if optional else '(必需)'}")
                print(f"    默认值: {default}")
                print(f"    说明: {param_help}")

        # 显示*args和**kwargs信息
        if 'accepts_args' in cmd_info:
            print(f"  *args: {cmd_info['accepts_args']}")
        if 'accepts_kwargs' in cmd_info:
            print(f"  **kwargs: {cmd_info['accepts_kwargs']}")

    def _tokenize_input(self, user_input: str) -> List[Any]:
        """将用户输入分割为 tokens，处理引号、转义字符、变量替换和 key=value 格式

        Args:
            user_input: 用户输入的字符串

        Returns:
            分割后的 tokens 列表，包含字符串和字典（用于 key=value 格式）
        """
        tokens = []
        current_token = []
        key = ''
        in_quote = None  # 当前引号类型：None, " or '
        escape_next = False  # 是否转义下一个字符
        value_process = False  # 是否在处理key的值

        def finish_token():
            """完成当前 token 的处理并添加到 tokens 列表"""
            nonlocal current_token, value_process, key
            token_str = ''.join(current_token)
            if value_process:
                tokens.append({key: token_str})
                value_process = False
            else:
                tokens.append(token_str)
            current_token = []

        i = 0
        while i < len(user_input):
            char = user_input[i]

            if escape_next:
                # 处理转义字符
                if char == 'n':
                    current_token.append('\n')
                elif char == 't':
                    current_token.append('\t')
                else:
                    # 处理 \', \", \\
                    current_token.append(char)
                escape_next = False
                i += 1
            elif char == '\\':
                # 开始转义序列
                escape_next = True
                i += 1
            elif in_quote:
                if char == in_quote:
                    # 结束引号
                    in_quote = None
                    finish_token()
                else:
                    current_token.append(char)
                i += 1
            elif char in ['"', "'"]:
                # 开始引号
                in_quote = char
                i += 1
            elif char == '$' and not current_token:
                # 开始变量（只有在 token 开头）
                # 收集变量名（直到空格或结束）
                var_name = []
                i += 1  # 跳过 $
                while i < len(user_input) and not user_input[i].isspace():
                    var_name.append(user_input[i])
                    i += 1
                var_name_str = ''.join(var_name)
                var_value = PathResolver.get(self.namespace, var_name_str, '$' + var_name_str)
                # 将变量值按空格分割并添加到 tokens
                if value_process:
                    tokens.append({key: var_value})
                    value_process = False
                else:
                    tokens.append(var_value)
            elif char == '=' and current_token:
                # 处理 key=value 格式
                key = ''.join(current_token)
                current_token = []
                i += 1  # 跳过 =
                value_process = True
            elif char.isspace():
                # 结束当前 token
                if current_token:
                    finish_token()
                i += 1
            else:
                current_token.append(char)
                i += 1

        # 添加最后一个 token
        if current_token:
            finish_token()

        return tokens

    def parse(self, user_input: str) -> Any:
        """解析用户输入并执行相应命令

        Args:
            user_input: 用户输入的字符串

        Returns:
            则返回函数执行结果

        Raises:
            ValueError: 当命令不存在或参数错误时
            TypeError: 当参数类型错误时
            Exception: 当命令执行出错时
        """
        # 检查是否是空输入
        if not user_input.strip():
            return None

        # 使用新的 tokenize 方法
        tokens = self._tokenize_input(user_input.strip())
        if not tokens:
            return None

        cmd = tokens[0]
        args = tokens[1:]

        # 解析别名
        if isinstance(cmd, str):
            cmd = self.resolve_command(cmd)
        else:
            # 如果第一个 token 是字典（key=value），则不是命令
            raise NotACommand('不是命令')

        # 处理命令
        if cmd not in self.commands:
            raise NotACommand('不是命令')

        cmd_info = self.commands[cmd]
        func = cmd_info['func']
        params_info = cmd_info['params']
        param_names = list(params_info.keys())
        accepts_args = cmd_info['accepts_args']
        accepts_kwargs = cmd_info['accepts_kwargs']

        def process_param(param_name: str, param_info: ProcessedParamInfo, arg_value: str) -> Any:
            """处理并转换参数值

            Args:
                param_name: 参数名称
                param_info: 参数信息字典
                arg_value: 参数值

            Returns:
                转换后的参数值

            Raises:
                TypeError: 当参数类型转换失败时
            """
            # 类型转换，默认为字符串类型
            param_type = param_info['type']

            if isinstance(arg_value, param_type):
                return arg_value

            try:
                if param_type == bool:
                    # 布尔值特殊处理
                    return arg_value.lower() in ('true', '1', 'yes', 'y')
                else:
                    return param_type(arg_value)
            except (ValueError, TypeError):
                raise TypeError(f"参数 {param_name} 需要 {param_type.__name__} 类型")

        def try_convert_type(value: str) -> Any:
            """尝试将字符串值转换为合适的类型

            Args:
                value: 要转换的字符串值

            Returns:
                转换后的值
            """
            try:
                # 尝试推断类型（默认为字符串）
                if value.isdigit():
                    return int(value)
                elif value.replace('.', '', 1).isdigit() and value.count('.') < 2:
                    return float(value)
                elif value.lower() in ('true', 'false'):
                    return value.lower() == 'true'
                else:
                    return value
            except (ValueError, AttributeError):
                return value

        # 初始化参数存储
        kwargs = {}  # 存储命名参数
        args_list = []  # 用于存储*args参数
        keyword_args = {}  # 用于存储**kwargs参数

        # 分离关键字参数和位置参数
        keyword_args_input = {}
        positional_args = []

        for arg in args:
            if isinstance(arg, dict):
                # 这是 key=value 格式的参数
                for k, v in arg.items():
                    if k in keyword_args_input:
                        raise ParamError(f"参数 {k} 被多次指定")
                    keyword_args_input[k] = v
            else:
                positional_args.append(arg)

        # 第一步：处理所有关键字参数
        for param_name, param_value in keyword_args_input.items():
            if param_name in params_info:
                param_info = params_info[param_name]
                kwargs[param_name] = process_param(param_name, param_info, param_value)
            elif accepts_kwargs:
                # 如果是**kwargs参数，直接存储为字符串
                keyword_args[param_name] = param_value
            else:
                raise ParamError(f"未知参数: {param_name}")

        # 第二步：处理位置参数，分配给未指定的命名参数
        # 确定哪些命名参数可以被位置参数指定
        positionable_params = [
            param_name for param_name in param_names 
            if param_name not in kwargs and not params_info[param_name]['keyword_only']
        ]

        # 处理位置参数
        for i, arg_value in enumerate(positional_args):
            if i < len(positionable_params):
                # 分配给可被位置参数指定的参数
                param_name = positionable_params[i]
                param_info = params_info[param_name]
                kwargs[param_name] = process_param(param_name, param_info, arg_value)
            elif accepts_args:
                # 如果是*args参数，尝试进行类型转换
                args_list.append(try_convert_type(arg_value))
            else:
                raise ParamError(f"参数过多，最多支持 {len(positionable_params)} 个位置参数")

        # 检查必需参数（只检查命名参数，*args参数不参与必需性检查）
        for param_name, param_info in params_info.items():
            if not param_info['optional'] and param_name not in kwargs:
                raise ParamError(f"缺少必需参数: {param_name}")

        # 执行命令函数
        merged_kwargs = {**kwargs, **keyword_args}
        return func(*args_list, **merged_kwargs)

    def _process_command_info(self, command_info: CommandInfo) -> ProcessedCommandInfo:
        """处理命令信息，补充可选键并分离多功能键，完全预生成帮助信息"""
        # 处理参数信息
        processed_params: Dict[str, ProcessedParamInfo] = {}
        if 'params' in command_info:
            for param_name, param_info in command_info['params'].items():
                # 有默认值的参数默认不被位置参数指定
                keyword_only = param_info.get('keyword_only', False)
                if 'default' in param_info:
                    keyword_only = param_info.get('keyword_only', True)

                processed_params[param_name] = {
                    'type': param_info.get('type', str),
                    'default': param_info.get('default', None),
                    'optional': 'default' in param_info,
                    'keyword_only': keyword_only
                }

        # 处理 accepts_args 和 accepts_kwargs
        accepts_args = 'accepts_args' in command_info
        accepts_kwargs = 'accepts_kwargs' in command_info

        # 预生成简短帮助信息（包括参数和*args/**kwargs指示）
        short_help_parts = []

        # 添加命令名称
        # 注意：这里我们不添加命令名称，因为命令列表显示时会单独显示命令名称
        # short_help_parts.append(cmd_name)

        # 添加参数信息
        params_str = ' '.join([
            f"[{param_name}{'?' if param_info['optional'] else ''}]" 
            for param_name, param_info in processed_params.items()
        ])

        if params_str:
            short_help_parts.append(params_str)

        # 添加*args和**kwargs指示
        if accepts_args:
            short_help_parts.append("[*args]")
        if accepts_kwargs:
            short_help_parts.append("[**kwargs]")

        # 添加命令说明
        original_help_text = command_info.get('help', '无说明')
        help_text = original_help_text
        # 截断到第一个换行符
        if '\n' in help_text:
            help_text = help_text.split('\n')[0]

        if short_help_parts:
            short_help = f"{' '.join(short_help_parts)} - {help_text}"
        else:
            short_help = f"- {help_text}"

        # 生成完整的帮助信息
        full_help = f"{original_help_text}\n\n"

        params = processed_params
        if params:
            full_help += "参数:\n"
            for param_name, param_info in params.items():
                full_help += f"  {param_name}: {param_info['type'].__name__} ({'可选' if param_info['optional'] else '必需'})\n"
                if param_info['optional']:
                    full_help += f"    默认值: {param_info['default']}\n"
                else:
                    full_help += f"    默认值: 无默认值\n"

                # 尝试从原始 command_info 中获取参数的 help
                original_param_help = command_info.get('params', {}).get(param_name, {}).get('help')
                if original_param_help:
                    full_help += f"    说明: {original_param_help}\n"

        if accepts_args:
            full_help += f"\n可变位置参数 (*args):\n  说明: {command_info.get('accepts_args', '无说明')}\n"
        if accepts_kwargs:
            full_help += f"\n可变关键字参数 (**kwargs):\n  说明: {command_info.get('accepts_kwargs', '无说明')}\n"

        if 'return_info' in command_info:
            full_help += f"\n返回值: {command_info['return_info']}"

        return {
            'func': command_info['func'],
            'params': processed_params,
            'accepts_args': accepts_args,
            'accepts_kwargs': accepts_kwargs,
            'short_help': short_help,
            'full_help': full_help.strip()
        }

    def add_command(self, command_name: str, command_info: CommandInfo) -> None:
        """添加命令到解析器

        Args:
            command_name: 命令名称
            command_info: 命令信息字典

        Raises:
            ValueError: 当命令已存在时
        """
        if command_name in self.commands:
            raise ValueError(f"命令 '{command_name}' 已存在")

        self.commands[command_name] = self._process_command_info(command_info)

    def remove_command(self, command_name: str) -> None:
        """从解析器移除命令

        Args:
            command_name: 命令名称

        Raises:
            ValueError: 当命令不存在时
        """
        if command_name not in self.commands:
            raise NotACommand(f"命令 '{command_name}' 不存在")

        # 移除所有指向该命令的别名
        aliases_to_remove = [
            alias for alias, cmd in self.aliases.items()
            if cmd == command_name
        ]

        for alias in aliases_to_remove:
            del self.aliases[alias]

        del self.commands[command_name]


def parse_google_docstring(docstring: Optional[str]) -> Tuple[str, Dict[str, str], Optional[str]]:
    """解析 Google 风格的文档字符串

    Args:
        docstring: 要解析的文档字符串

    Returns:
        Tuple[命令帮助信息, 参数字典, 返回信息]
    """
    if not docstring:
        return "无说明", {}, None

    # 清理文档字符串
    docstring = docstring.strip()

    # 提取命令帮助信息（Args 之前的内容）
    help_info = ""
    args_section = re.search(r'^\s*Args:\s*$', docstring, re.MULTILINE)
    if args_section:
        help_info = docstring[:args_section.start()].strip()
    else:
        # 如果没有 Args 部分，整个文档字符串都是帮助信息
        help_info = docstring

    # 提取参数信息
    params_info = {}
    if args_section:
        # 查找 Args 部分
        args_start = args_section.end()

        # 查找下一个节（Returns 或 Raises）
        next_section = re.search(r'^\s*(?:Returns|Raises):\s*$', docstring[args_start:], re.MULTILINE)
        if next_section:
            args_text = docstring[args_start:args_start + next_section.start()]
        else:
            args_text = docstring[args_start:]

        # 解析参数行
        param_pattern = r'^\s*(\w+):\s*(.*?)(?=\n\s*\w+:|$|\n\s*$)'
        for match in re.finditer(param_pattern, args_text, re.MULTILINE | re.DOTALL):
            param_name, param_help = match.groups()
            params_info[param_name.strip()] = param_help.strip()

    # 提取返回信息
    return_info = None
    returns_section = re.search(r'^\s*Returns:\s*$', docstring, re.MULTILINE)
    if returns_section:
        returns_start = returns_section.end()

        # 查找下一个节（Raises）或文档结束
        next_section = re.search(r'^\s*Raises:\s*$', docstring[returns_start:], re.MULTILINE)
        if next_section:
            returns_text = docstring[returns_start:returns_start + next_section.start()]
        else:
            returns_text = docstring[returns_start:]

        return_info = returns_text.strip()

    return help_info, params_info, return_info

def infer_command_info(func: Callable, **overrides) -> CommandInfo:
    """从函数签名和文档字符串推断 CommandInfo"""
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)

    # 解析文档字符串
    help_info, params_doc, return_info = parse_google_docstring(func.__doc__)

    # 构建参数字典
    params = {}
    for param_name, param in sig.parameters.items():
        # 跳过 self 和 cls 参数
        if param_name in ('self', 'cls'):
            continue

        param_info = {}

        # 从类型提示获取类型
        if param_name in type_hints:
            param_info['type'] = type_hints[param_name]

        # 从默认值判断是否为可选参数
        if param.default != param.empty:
            param_info['default'] = param.default
            param_info['keyword_only'] = True  # 有默认值的参数默认只能通过关键字指定

        # 从文档字符串获取参数帮助信息
        if param_name in params_doc:
            param_info['help'] = params_doc[param_name]

        params[param_name] = param_info

    # 检查是否有 *args 和 **kwargs
    has_var_args = any(
        p.kind == p.VAR_POSITIONAL for p in sig.parameters.values()
    )
    has_var_kwargs = any(
        p.kind == p.VAR_KEYWORD for p in sig.parameters.values()
    )

    # 构建基本 CommandInfo
    cmd_info: CommandInfo = {
        'func': func,
        'params': params,
        'help': overrides.get('help', help_info)
    }

    # 添加返回信息
    if return_info:
        cmd_info['return_info'] = return_info

    if has_var_args:
        cmd_info['accepts_args'] = overrides.get('accepts_args', '可变位置参数')

    if has_var_kwargs:
        cmd_info['accepts_kwargs'] = overrides.get('accepts_kwargs', '可变关键字参数')

    return cmd_info
