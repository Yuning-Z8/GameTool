class GameOver(Exception):
    """游戏结束异常，用于终止游戏循环"""
    pass


class PermissionDenied(Exception):
    """权限拒绝异常，表示操作未被授权"""
    pass


class NotACommand(Exception):
    """不是一个命令"""
    pass


class ParamError(Exception):
    """参数错误"""
    pass

class UnKnowError(Exception):
    pass