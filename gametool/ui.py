import re
from typing import List, Generator, Union

from . import basic
from .basic import FULL_WIDTH_CHAR_RANGE, CHINESE_CHAR_RANGE, ANSI_ESCAPE_RE


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
        self.contents: List[str] = []  # 存储界面内容的列表

    def text(self, message: str) -> 'UI':
        """添加普通信息文本到界面
        
        Args:
            message: 要显示的信息文本
            
        Returns:
            返回self以支持链式调用
        """
        self.contents += self._format_output([message], self.width)
        return self

    def split_text(self, left_content: str, right_content: str = '0: 返回', filler: str = ' ') -> 'UI':
        """
        创建左右分栏的内容行
        
        Args:
            left_content: 左侧内容
            right_content: 右侧内容（默认返回选项）
            filler: 填充字符（默认空格）
            
        Returns:
            返回self以支持链式调用
        """
        # 计算右侧文本的位置，确保标题文本和右侧文本正确对齐
        back_part = filler * int((self.width - display_width(left_content) - display_width(right_content)) // display_width(filler)) + right_content if right_content else ''
        title_line = left_content + back_part
        self.contents.append(title_line)
        return self

    def choice(self, options: List[str], block_size: int = 1000, addnum: bool = True, startnum: int = 1) -> 'UI':
        """添加选项列表到界面
        
        Args:
            options: 选项文本列表
            block_size: 每个选项块的显示宽度，默认为1000
            addnum: 是否自动添加编号，默认为True
            startnum: 起始编号，默认为1
            
        Returns:
            返回self以支持链式调用
        """
        if addnum:
            # 为选项添加编号
            for i in range(len(options)):
                options[i] = f'{startnum}: ' + options[i]
                startnum += 1
        self.contents += self._format_output(options, block_size)
        return self
    
    def line(self, char: str) -> 'UI':
        """添加分割线到界面
        
        Args:
            char: 用于组成分割线的字符
            
        Returns:
            返回self以支持链式调用
        """
        self.contents.append(char * (self.width//display_width(char)))
        return self
    
    def center_text(self, text: str, fillchar: str = ' ') -> 'UI':
        """添加居中显示的文本
        
        Args:
            text: 要居中显示的文本
            fillchar: 填充字符，默认为空格
            
        Returns:
            返回self以支持链式调用
        """
        text_width = display_width(text)
        if text_width >= self.width:
            self.contents.append(text)
        else:
            padding = int((self.width - text_width) / display_width(fillchar) // 2)
            centered = fillchar * padding + text + fillchar * padding
            # 调整奇数宽度的情况
            if len(centered) < self.width:
                centered += fillchar
            self.contents.append(centered)
        return self

    def clean(self) -> 'UI':
        """清除当前所有界面内容
        
        Returns:
            返回self以支持链式调用
        """
        self.contents = []
        return self
    
    def flush(self) -> str:
        """获取格式化后的完整界面字符串
        
        Returns:
            拼接所有内容后的完整字符串
        """
        return '\n'.join(self.contents)

    def copy(self) -> 'UI':
        """创建当前UI对象的副本
        
        Returns:
            新的UI实例，包含当前所有内容
        """
        ui = UI(self.width)
        ui.contents = self.contents.copy()
        return ui

        
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
        ui.contents = self.contents + other.contents
        return ui
    
    # 兼容区

    def header(self, text, right = '0: 返回'):
        """（已废弃）请改用 split_line"""
        return self.split_text(text, right)
    
    def info(self, message):
        """（已废弃）请改用 text"""
        return self.text(message)
    
    def center(self, text, fillchar = ' '):
        """（已废弃）请改用 center_text"""
        return self.center_text(text, fillchar)


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
            width += 100
        else:
            width += 50
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
