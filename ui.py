from typing import List, Union

import basic


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

    def info(self, message: str) -> 'UI':
        """添加普通信息文本到界面
        
        Args:
            message: 要显示的信息文本
            
        Returns:
            返回self以支持链式调用
        """
        self.contents.append(self._format_output([message], self.width))
        return self

    def header(self, text: str, right_aligned: str = '0: 返回') -> 'UI':
        """添加标题到界面
        
        Args:
            text: 标题文本
            right_aligned: 返回选项文本，默认为'0: 返回'
            
        Returns:
            返回self以支持链式调用
        """
        # 计算右侧文本的位置，确保标题文本和右侧文本正确对齐
        back_part = ' ' * int((self.width - display_width(text) - display_width(right_aligned)) // display_width(' ')) + right_aligned if right_aligned else ''
        title_line = text + back_part + '\n'
        self.contents.append(title_line)
        return self

    def choice(self, options: List[str], block_size: int = 10, addnum: bool = True, startnum: int = 1) -> 'UI':
        """添加选项列表到界面
        
        Args:
            options: 选项文本列表
            block_size: 每个选项块的显示宽度，默认为10
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
        self.contents.append(self._format_output(options, block_size))
        return self
    
    def line(self, char: str) -> 'UI':
        """添加分割线到界面
        
        Args:
            char: 用于组成分割线的字符
            
        Returns:
            返回self以支持链式调用
        """
        self.contents.append(char * int(self.width//display_width(char)) + '\n')
        return self
    
    def center(self, text: str, fillchar: str = ' ') -> 'UI':
        """添加居中显示的文本
        
        Args:
            text: 要居中显示的文本
            fillchar: 填充字符，默认为空格
            
        Returns:
            返回self以支持链式调用
        """
        text_width = display_width(text)
        if text_width >= self.width:
            self.contents.append(text + '\n')
        else:
            padding = int((self.width - text_width) / display_width(fillchar) // 2)
            centered = fillchar * padding + text + fillchar * padding
            # 调整奇数宽度的情况
            if len(centered) < self.width:
                centered += fillchar
            self.contents.append(centered + '\n')
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
        return ''.join(self.contents)

    def copy(self) -> 'UI':
        """创建当前UI对象的副本
        
        Returns:
            新的UI实例，包含当前所有内容
        """
        ui = UI(self.width)
        ui.contents = self.contents.copy()
        return ui

        
    def _format_output(self, input_word_group: List[str], len_block: int) -> str:
        """格式化输出文本，将文本分组并按指定宽度排列
        
        Args:
            input_word_group: 输入文本列表
            len_block: 每个文本块的显示宽度
            long: 总显示宽度
            
        Returns:
            格式化后的字符串
        """
        num = self.width // len_block  # 计算每行可以容纳的块数
        cnt_block = 0  # 当前行已添加的块数
        opt = ''  # 当前行正在构建的内容
        res = ''  # 最终结果
        
        for line in input_word_group:
            for word in self._block_divide(line, len_block):
                opt += word
                cnt_block += 1
                if cnt_block == num:  # 当前行已满
                    res += opt + '\n'
                    opt = ''
                    cnt_block = 0
                    
        if opt:  # 添加剩余内容
            res += opt + '\n'
        return res

    def _block_divide(self, text: str, length: int) -> List[str]:
        """将文本分割为指定长度的块，考虑字符显示宽度
        
        Args:
            text: 要分割的文本
            length: 每个块的显示宽度
            
        Returns:
            分割后的文本块列表
        """
        result = []
        current = ''  # 当前正在构建的块
        current_width = 0  # 当前块的显示宽度
        
        for char in text:
            char_width = display_width(char)
            if current_width + char_width > length:  # 当前块已超过长度限制
                if current:
                    result.append(current)
                    current = ''
                    current_width -= length
                    
            current += char
            current_width += char_width
            
        if current:  # 添加最后一个块
            while display_width(current) < length:
                current += ' '  # 用空格填充不足部分
            result.append(current)
            
        return result
    
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

def display_width(text: str) -> float:
    """计算字符串的实际显示宽度
    
    Args:
        text: 要计算的字符串
        
    Returns:
        字符串的显示宽度
    """
    if basic.is_equal_width_font:
        return _display_width_of_equal_width_font(text)
    else:
        return _display_width_of_non_equal_width_font(text)

def _display_width_of_equal_width_font(text: str) -> float:
    """计算字符串在等宽字体中的显示宽度
    
    全角字符（如中文、日文、韩文、全角符号、emoji等）计为2个宽度，
    半角字符计为1个宽度。
    
    Args:
        text: 要计算的字符串
        
    Returns:
        字符串的显示宽度
    """
    width = 0
    for char in text:
        # 检查字符是否属于全角字符范围
        if is_in_range(char, basic.FULL_WIDTH_CHAR_RANGE):
            width += 1
        else:
            width += 0.5
    return width

def _display_width_of_non_equal_width_font(text: str) -> float:
    """计算字符串在非等宽字体中的显示宽度
    
    Args:
        text: 要计算的字符串
        
    Returns:
        字符串的显示宽度
    """
    width = 0.0
    for char in text:
        # 检查是否在映射表中
        if char in basic.CHAR_WIDTH_MAPS[basic.font]:
            width += basic.CHAR_WIDTH_MAPS[basic.font][char]
        # 检查是否为中文字符
        elif is_in_range(char, basic.CHINESE_CHAR_RANGE):
            # 中文字符默认宽度（可根据实际字体调整）
            width += 1
        else:
            # 其他字符默认宽度
            width += 0.5
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
