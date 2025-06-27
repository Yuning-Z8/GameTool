import basic


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

def intinput(prompt: str, max_: int = 20, min_: int = 0) -> int:
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
            a = int(a)  # 尝试将输入转换为整数
            if min_ <= a <= max_: 
                return a  # 输入有效，返回整数
            else: 
                raise ValueError  # 输入超出范围
        except ValueError:
            # 处理无效输入（非整数或超出范围）
            yinput('请输入有效数字！')
