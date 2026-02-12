import re
from typing import List, Tuple, Generator, Union, Callable, Optional

from . import basic
from .basic import FULL_WIDTH_CHAR_RANGE, ANSI_ESCAPE_RE


class ANSI:
    """ANSI转义序列类定义，新增offstyle类管理样式关闭选项"""

    # 前景非亮色（直接访问）
    black = "\033[30m"
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    magenta = "\033[35m"
    cyan = "\033[36m"
    white = "\033[37m"

    # 前景亮色
    class fglight:
        black = "\033[90m"
        red = "\033[91m"
        green = "\033[92m"
        yellow = "\033[93m"
        blue = "\033[94m"
        magenta = "\033[95m"
        cyan = "\033[96m"
        white = "\033[97m"

    # 背景非亮色
    class bg:
        black = "\033[40m"
        red = "\033[41m"
        green = "\033[42m"
        yellow = "\033[43m"
        blue = "\033[44m"
        magenta = "\033[45m"
        cyan = "\033[46m"
        white = "\033[47m"

    # 背景亮色
    class bglight:
        black = "\033[100m"
        red = "\033[101m"
        green = "\033[102m"
        yellow = "\033[103m"
        blue = "\033[104m"
        magenta = "\033[105m"
        cyan = "\033[106m"
        white = "\033[107m"

    # 文本样式（开启）
    class style:
        bold = "\033[1m"        # 加粗
        dim = "\033[2m"         # 暗淡
        italic = "\033[3m"      # 斜体
        underline = "\033[4m"   # 下划线
        blink = "\033[5m"       # 闪烁
        invert = "\033[7m"      # 前景/背景互换
        hidden = "\033[8m"      # 隐藏
        strikethrough = "\033[9m"  # 删除线

        # 文本样式（关闭）
        class off:
            bold = "\033[21m"       # 关闭加粗
            dim = "\033[22m"        # 关闭暗淡
            italic = "\033[23m"     # 关闭斜体
            underline = "\033[24m"  # 关闭下划线
            blink = "\033[25m"      # 关闭闪烁
            invert = "\033[27m"     # 关闭前景/背景互换
            hidden = "\033[28m"     # 关闭隐藏
            strikethrough = "\033[29m"  # 关闭删除线

    class cursor:
        """光标控制"""
        up = lambda n=1: f"\033[{n}A"       # 上移n行
        down = lambda n=1: f"\033[{n}B"     # 下移n行
        right = lambda n=1: f"\033[{n}C"    # 右移n列
        left = lambda n=1: f"\033[{n}D"     # 左移n列
        home = "\033[H"                     # 移动到左上角
        position = lambda x, y: f"\033[{y};{x}H"  # 移动到(x,y)位置
        save = "\033[s"                     # 保存光标位置
        restore = "\033[u"                  # 恢复光标位置

    class screen:
        """屏幕控制"""
        clear = "\033[2J"                   # 清屏
        clear_line = "\033[K"               # 清除当前行
        clear_to_end = "\033[0J"            # 清除从光标到屏幕结尾
        clear_to_start = "\033[1J"          # 清除从光标到屏幕开头

    class preset:
        @property
        def success(self):
            return ANSI.combine(ANSI.green, ANSI.style.bold)

        @property
        def error(self):
            return ANSI.combine(ANSI.red, ANSI.style.bold)

        @property
        def warning(self):
            return ANSI.combine(ANSI.yellow)

        @property
        def info(self):
            return ANSI.combine(ANSI.blue)

        @property
        def highlight(self):
            return ANSI.combine(ANSI.style.invert, ANSI.style.bold)

        @property
        def debug(self):
            return ANSI.combine(ANSI.fglight.black)

    # 全局重置（清除所有样式）
    reset = "\033[0m"

    class rgb:
        """8位RGB支持（r, g, b范围0-255）"""
        @staticmethod
        def fg(r: int, g: int, b: int) -> str:
            return f"\033[38;2;{r};{g};{b}m"

        @staticmethod
        def bg(r: int, g: int, b: int) -> str:
            return f"\033[48;2;{r};{g};{b}m"

    @staticmethod
    def combine(*styles):
        """组合多个样式为一个字符串"""
        return ''.join(styles)


class UI:
    """用户界面类，用于构建和显示格式化的控制台界面

    该类提供了一系列方法用于创建结构化的控制台界面，
    支持标题、信息文本、选项列表、分割线等元素的组合排列。
    考虑了不同字符宽度的显示问题，支持等宽和非等宽字体。
    """

    def __init__(self, width: Union[int, None] = None) -> None:
        """初始化UI实例

        Args:
            width: UI显示宽度，默认为basic模块中的ui_width
        """
        self.width = basic.ui_width if width is None else width  # UI的显示宽度，单位为全角字符
        self.items:List[Tuple[Callable, Tuple, bool]] = []
        self.lines: List[str] = []
        self.father: Optional['UI'] = None  # 父UI引用，默认为None
        self.static_cache: dict[Tuple[Callable, Tuple], List[str]] = {}  # 静态内容缓存，用于存储不变的文本内容
        self.dynamic_cache: dict[Tuple[Callable, Tuple], Tuple[List, List[str]]] = {}  # 动态内容缓存，用于存储可能变化的文本内容

    def text(self, message: str | Callable[..., str], cache: bool = True) -> 'UI':
        """添加普通信息文本到界面

        Args:
            message: 要显示的信息文本
            cache: 是否缓存该文本内容，默认为True
        Returns:
            返回self以支持链式调用
        """
        self.items.append((self._text_render, (message,), cache))
        return self

    def text_line(self, left_content: str | Callable[..., str] = '', center_content: str | Callable[..., str] = '', right_content: str | Callable[..., str] = '', filler: str = ' ', cache: bool = True) -> 'UI':
        """
        创建带有左、中、右对齐内容的单行文本

        Args:
            left_content: 左侧内容
            center_content
            right_content: 右侧内容
            filler: 填充字符（默认空格）
            cache: 是否缓存该文本内容，默认为True

        Returns:
            返回self以支持链式调用
        """
        self.items.append((self._text_line_render, (left_content, center_content, right_content, filler), cache))
        return self

    def choice(self, options: List[str] | Callable[..., List[str]], block_size: int = 1000, addnum: bool = True, startnum: int = 1, cache: bool = True) -> 'UI':
        """添加选项列表到界面

        Args:
            options: 选项文本列表
            block_size: 每个选项块的显示宽度，默认为1000
            addnum: 是否自动添加编号，默认为True
            startnum: 起始编号，默认为1
            cache: 是否缓存该选项列表内容，默认为True

        Returns:
            返回self以支持链式调用
        """
        self.items.append((self._choice_render, (options, block_size, addnum, startnum), cache))
        return self

    def sub_ui(self, sub_ui: Optional['UI'] = None, cache: bool = False) -> 'UI':
        """将子UI渲染结果添加到当前UI中

        Args:
            sub_ui: 要嵌入的子UI对象
            cache: 是否缓存该子UI内容，默认为False
        Returns:
            返回self以支持链式调用
        """
        if sub_ui is None:
            sub_ui = UI(self.width - 2)  # 减去2个字符宽度用于边框显示
        self.items.append((self._sub_ui_render, (sub_ui,), cache))
        return sub_ui

    def render(self) -> list[str]:
        """获取格式化后的界面内容列表

        Returns:
            界面内容的字符串列表
        """
        result = []
        for item in self.items:
            dynamic = False  # 标记是否存在动态内容
            func, args, cache = item
            processed_args = []
            for arg in item[1]:
                if callable(arg):
                    dynamic = True
                    processed_args.append(arg())  # 如果参数是可调用的，调用它并替换为结果
                else:
                    processed_args.append(arg)
            if not cache:  # 如果不需要缓存，直接渲染
                result += func(*processed_args)
                continue
            cache_key = (func, args)
            if dynamic:
                if cache_key in self.dynamic_cache and self.dynamic_cache[cache_key][0] == processed_args:
                    result += self.dynamic_cache[cache_key][1]
                    continue
                result_ = func(*processed_args)
                self.dynamic_cache[cache_key] = (processed_args, result_)
            else:
                if cache_key in self.static_cache:
                    result += self.static_cache[cache_key]
                    continue
                result_ = func(*processed_args)
                self.static_cache[cache_key] = result_
        self.lines = result
        return result

    def clean(self) -> 'UI':
        """清除当前所有界面内容

        Returns:
            返回self以支持链式调用
        """
        self.items = []
        self.static_cache.clear()
        self.dynamic_cache.clear()
        return self

    def flush(self) -> str:
        """获取格式化后的完整界面字符串

        Returns:
            拼接所有内容后的完整字符串
        """
        return '\n'.join(self.lines)

    def copy(self) -> 'UI':
        """创建当前UI对象的副本

        Returns:
            新的UI实例，包含当前所有内容
        """
        ui = UI(self.width)
        ui.items = self.items.copy()
        return ui


    def _text_render(self, message: str) -> list[str]:
        """添加普通信息文本到界面

        Args:
            message: 要显示的信息文本

        Returns:
            返回self以支持链式调用
        """
        return self._format_output([message], self.width)

    def _text_line_render(self, left_content: str = '', center_content: str = '', right_content: str = '', filler: str = ' ') -> list[str]:
        """
        创建带有左、中、右对齐内容的单行文本

        Args:
            left_content: 左侧内容
            center_content
            right_content: 右侧内容
            filler: 填充字符（默认空格）

        Returns:
            返回self以支持链式调用
        """
        left_width, center_width, right_width = display_width(left_content), display_width(center_content), display_width(right_content)
        center_remain = self.width - left_width - right_width
        if center_remain - center_width < 0:
            return ['WEDTH IS NOT ENOUGH']
        hife_width = self.width / 2
        filler_width = display_width(filler)
        center = 1 - center_width / center_remain
        left_filler_count = round((hife_width - left_width) * center / filler_width)
        right_filler_count = round((hife_width - right_width) * center / filler_width)
        if (left_filler_count or right_filler_count) < 0:
            fix = (left_filler_count + right_filler_count) // 2
            left_filler_count -= fix
            right_filler_count += fix
            if left_filler_count <= 0:
                right_filler_count += left_filler_count
                if right_filler_count > 1:
                    left_filler_count = 1
                    right_filler_count -= 1
            if right_filler_count <= 0:
                left_filler_count += right_filler_count
                if left_filler_count > 1:
                    right_filler_count = 1
                    left_filler_count -= 1
        return [''.join([left_content, filler * left_filler_count, center_content, filler * right_filler_count, right_content])]

    def _choice_render(self, options: List[str], block_size: int = 1000, addnum: bool = True, startnum: int = 1) -> list[str]:
        """添加选项列表到界面

        Args:
            options: 选项文本列表
            block_size: 每个选项块的显示宽度，默认为1000
            addnum: 是否自动添加编号，默认为True
            startnum: 起始编号，默认为1

        Returns:
            返回self以支持链式调用
        """
        result = []
        if addnum:
            # 为选项添加编号
            for i in range(len(options)):
                options[i] = f'{startnum}: ' + options[i]
                startnum += 1
        result += self._format_output(options, block_size)
        return result

    def _sub_ui_render(self, sub_ui: 'UI') -> list[str]:
        """将子UI渲染结果添加到当前UI中"""
        result = self._text_line_render(right_content='┐', filler='─')
        for line in sub_ui.render():
            result.append(f"{line}│")
        result += self._text_line_render(right_content='┘', filler='─')
        return result

    def _format_output(self, input_word_group: List[str], len_block: int) -> List[str]:
        """格式化输出文本，将文本分组并按指定宽度排列

        Args:
            input_word_group: 输入文本列表
            len_block: 每个文本块的显示宽度

        Returns:
            格式化后的字符串列表
        """
        num = self.width // len_block  # 计算每行可以容纳的块数
        opt = []  # 当前行正在构建的内容
        res = []  # 最终结果

        for text in input_word_group:
            for word in self._block_divide(text, len_block):
                opt.append(word)
                if len(opt) == num:  # 当前行已满
                    res.append(''.join(opt))
                    opt = []

        if opt:  # 添加剩余内容
            res.append(''.join(opt))
        return res

    def _block_divide(self, text: str, length: int) -> Generator[str, None, None]:
        """将文本分割为指定长度的块，考虑字符显示宽度

        Args:
            text: 要分割的文本
            length: 每个块的显示宽度

        Returns:
            分割后的文本块生成器
        """
        # 先移除ANSI转义序列以计算实际显示宽度
        clean_text = ANSI_ESCAPE_RE.sub('', text)

        # 跟踪ANSI转义序列的状态
        ansi_state = ""
        current = []  # 当前正在构建的块
        current_width = 0  # 当前块的显示宽度

        i = 0
        while i < len(text):
            char = text[i]

            # 检查是否开始ANSI转义序列
            if char == '\x1b' and i + 1 < len(text) and text[i + 1] == '[':
                # 提取完整的ANSI转义序列
                j = i + 2
                while j < len(text) and text[j] not in 'ABCDEFGHJKSTfm':
                    j += 1
                if j < len(text):
                    ansi_seq = text[i:j+1]
                    ansi_state = ansi_seq  # 保存当前ANSI状态
                    current.append(ansi_seq)
                    i = j + 1
                    continue

            # 处理普通字符
            char_width = display_width(char)
            if current_width + char_width > length:  # 当前块已超过长度限制
                if current:
                    # 如果当前有活动的ANSI状态，确保在块结束时重置
                    if ansi_state:
                        current.append('\x1b[0m')
                    yield ''.join(current)
                    current = []
                    # 如果有活动的ANSI状态，在新块开始时恢复
                    if ansi_state:
                        current.append(ansi_state)
                    current_width = 0

            current.append(char)
            current_width += char_width
            i += 1

        if current:  # 添加最后一个块
            # 如果有活动的ANSI状态，确保在文本结束时重置
            if ansi_state:
                current.append('\x1b[0m')
            current += ' ' * ((length - current_width) // display_width(' '))  # 用空格填充不足部分
            yield ''.join(current)

    def __add__(self, other: 'UI') -> 'UI':
        """合并两个UI对象的内容

        Args:
            other: 要合并的另一个UI对象

        Returns:
            合并后的新UI对象

        Raises:
            ValueError: 如果两个UI的宽度不一致
        """
        if self.width != other.width:
            raise ValueError('UI宽度不一致')
        ui = UI(self.width)
        ui.items = self.items + other.items
        return ui


def is_in_range(char: str, range) -> bool:
    """检查字符是否在指定范围内

    Args:
        char: 要检查的字符
        range: 字符范围列表，每个范围由起始和结束码点组成

    Returns:
        如果字符在范围内返回True，否则返回False
    """
    code = ord(char)
    for start, end in range:
        if start <= code <= end:
            return True
    return False

# 修改display_width函数
def display_width(text: str) -> int:
    """计算字符串的显示宽度

    Args:
        text: 要计算的字符串，可以包含ANSI转义序列
    Returns:
        字符串的显示宽度（不包括ANSI转义序列）
    """
    # 移除ANSI转义序列后再计算宽度
    text = ANSI_ESCAPE_RE.sub('', text)

    width = 0
    for char in text:
        # 检查字符是否属于全角字符范围
        if is_in_range(char, FULL_WIDTH_CHAR_RANGE):
            width += 2
        else:
            width += 1
    return width

def bar(val: float, max_: float, lenth: int = 8, empty: str ='.', full: str = '#') -> str:
    """生成进度/占用条字符串

    Args:
        val: 当前值
        max_: 最大值
        lenth: 进度/占用条长度（字符数），默认为8
        empty: 未完成部分使用的字符，默认为'.'
        full: 已完成部分使用的字符，默认为'#'

    Returns:
        生成的进度条字符串
    """
    bar_ = full * int((val / max_) * lenth)
    bar_ = bar_.ljust(lenth, empty)
    return bar_
