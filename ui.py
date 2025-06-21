from typing import List

from basic import *


class UI:
    """用户界面类，用于构建和显示格式化的控制台界面
    
    属性:
        width (int): UI显示宽度（单位：半角字符）
        contents (List[str]): 存储界面内容的列表
    """
    
    def __init__(self, width: int = UI_WIDTH) -> None:
        """初始化UI实例
        
        Args:
            width: UI显示宽度，默认为UI_WIDTH
        """
        self.width = width
        self.contents: List[str] = []  # 存储界面内容的列表

    def info(self, message: str) -> 'UI':
        """添加普通信息文本到界面
        
        Args:
            message: 要显示的信息文本
            
        Returns:
            返回self以支持链式调用
        """
        self.contents.append(self._format_output([message], self.width, self.width))
        return self

    def header(self, text: str, right_aligned: str = '0: 返回') -> 'UI':
        """添加标题到界面
        
        Args:
            text: 标题文本
            right_aligned: 返回选项文本，默认为'0: 返回'
            
        Returns:
            返回self以支持链式调用
        """
        back_part = ' ' * (self.width - calculate_display_width(text) - calculate_display_width(right_aligned)) + right_aligned if right_aligned else ''
        title_line = text + back_part + '\n'
        self.contents.append(title_line)
        return self

    def choice(self, options: List[str], block_size: int = 20) -> 'UI':
        """添加选项列表到界面
        
        Args:
            options: 选项文本列表
            block_size: 每个选项块的显示宽度，默认为20
            
        Returns:
            返回self以支持链式调用
        """
        self.contents.append(self._format_output(options, block_size, self.width))
        return self
    
    def line(self, char: str) -> 'UI':
        """添加分割线到界面
        
        Args:
            char: 用于组成分割线的字符
            
        Returns:
            返回self以支持链式调用
        """
        self.contents.append(char * (self.width//calculate_display_width(char)) + '\n')
        return self
    
    def center(self, text: str, fillchar: str = ' ') -> 'UI':
        """添加居中显示的文本
        
        Args:
            text: 要居中显示的文本
            fillchar: 填充字符，默认为空格
            
        Returns:
            返回self以支持链式调用
        """
        text_width = calculate_display_width(text)
        if text_width >= self.width:
            self.contents.append(text + '\n')
        else:
            padding = (self.width - text_width) // 2
            # 确保填充字符是单宽度字符
            fillchar = fillchar[0] if fillchar else ' '
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
        return self
        
    def _format_output(self, input_word_group: List[str], len_block: int, long: int) -> str:
        """格式化输出文本，将文本分组并按指定宽度排列
        
        Args:
            input_word_group: 输入文本列表
            len_block: 每个文本块的显示宽度
            long: 总显示宽度
            
        Returns:
            格式化后的字符串
        """
        num = long // len_block  # 计算每行可以容纳的块数
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
            char_width = calculate_display_width(char)
            if current_width + char_width > length:  # 当前块已超过长度限制
                if current:
                    result.append(current)
                    current = ''
                    current_width -= length
                    
            current += char
            current_width += char_width
            
        if current:  # 添加最后一个块
            while calculate_display_width(current) < length:
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

def calculate_display_width(text: str) -> int:
    """计算字符串的实际显示宽度（考虑全角字符）
    
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
        if (ord(char) >= 0x4E00 and ord(char) <= 0x9FFF or   # 中日韩统一表意文字
           ord(char) >= 0xFF00 and ord(char) <= 0xFFEF or    # 全角符号
           ord(char) >= 0x2600 and ord(char) <= 0x26FF or    # 杂项符号
           ord(char) >= 0x2700 and ord(char) <= 0x27BF or    # 装饰符号
           ord(char) >= 0x1F300 and ord(char) <= 0x1F5FF or  # 象形文字
           ord(char) >= 0x1F600 and ord(char) <= 0x1F64F or  # Emoji表情
           ord(char) >= 0x1F680 and ord(char) <= 0x1F6FF):   # 交通和地图符号
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
