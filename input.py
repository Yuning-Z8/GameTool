from basic import *


def yinput(prompt: str) -> str:
    """带指令控制的输入函数
    
    Args:
        prompt: 提示信息
        
    Returns:
        用户输入的内容
    """
    user_input = input(prompt)
    if user_input in INPUT_ACT:
        INPUT_ACT[user_input]()
    return user_input

def intinput(prompt: str, max_: int = 20, min_: int = 0) -> int:
    """获取一个在指定范围内的整数输入
    
    Args:
        prompt: 提示信息
        max_: 最大值，默认为20
        min_: 最小值，默认为0
        
    Returns:
        用户输入的整数
        
    Note:
        会循环提示直到输入有效值
    """
    while True:
        try:
            a = yinput(prompt)
            a = int(a)
            if min_ <= a <= max_: 
                return a
            else: 
                raise ValueError
        except ValueError:
            yinput('请输入有效数字！')
