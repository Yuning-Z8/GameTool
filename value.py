from typing import Any, List, Union, Sequence

class PathResolver:
    """
    通用路径解析器，支持通过.分隔的路径或列表路径访问和修改各种类型对象的值
    
    支持的对象类型：
    - 列表/元组（通过索引访问，如"list.0"或["list", 0]）
    - 字典（通过键访问，如"dict.key"或["dict", "key"]， (不支持`'1':...`）
    - 类实例/模块（通过属性访问，如"obj.attr"或["obj", "attr"]）
    
    支持的路径格式：
    - 字符串路径："attr1.key.0"
    - 列表路径：["attr1", "key", 0]
    """
    
    @staticmethod
    def get(obj: Any, path: Union[str, List[Union[str, int]]], default: Any = None) -> Any:
        """
        通过路径获取对象中的值
        
        :param obj: 要访问的根对象
        :param path: 路径，可以是点分隔的字符串或包含字符串/整数的列表
        :param default: 路径不存在时返回的默认值
        :return: 路径指向的值或默认值
        """
        # 处理路径格式，统一转为列表形式
        parts = PathResolver._normalize_path(path)
        current = obj
        
        try:
            for part in parts:
                current = PathResolver._get_next(current, part)
            return current
        except (IndexError, KeyError, AttributeError):
            return default
    
    @staticmethod
    def set(obj: Any, path: Union[str, List[Union[str, int]]], value: Any) -> bool:
        """
        通过路径修改对象中的值
        
        :param obj: 要修改的根对象
        :param path: 路径，可以是点分隔的字符串或包含字符串/整数的列表
        :param value: 要设置的新值
        :return: 修改成功返回True，失败返回False
        """
        # 处理路径格式，统一转为列表形式
        parts = PathResolver._normalize_path(path)
        if not parts:
            return False
            
        # 获取倒数第二个部分的对象
        try:
            parent = obj
            for part in parts[:-1]:
                parent = PathResolver._get_next(parent, part)
            
            # 设置最后一个部分的值
            last_part = parts[-1]
            PathResolver._set_last(parent, last_part, value)
            return True
        except (IndexError, KeyError, AttributeError, TypeError):
            return False
    
    @staticmethod
    def _normalize_path(path: Union[str, List[Union[str, int]]]) -> Sequence[Union[str, int]]:
        """将路径统一转换为列表形式"""
        if isinstance(path, str):
            return path.split('.')
        elif isinstance(path, list):
            return path
        else:
            raise TypeError("路径必须是字符串或列表")
    
    @staticmethod
    def _get_next(current: Any, part: Union[str, int]) -> Any:
        """获取当前对象的下一级对象"""
        # 整数直接作为索引处理（用于列表/元组）
        if isinstance(part, int):
            return current[part]
        
        # 尝试将字符串部分解析为整数索引
        try:
            index = int(part)
            return current[index]
        except (ValueError, TypeError):
            pass  # 不是整数索引
        
        # 尝试作为字典键访问
        if isinstance(current, dict):
            return current[part]
        
        # 作为对象属性访问
        return getattr(current, part)
    
    @staticmethod
    def _set_last(parent: Any, part: Union[str, int], value: Any) -> None:
        """设置最后一级的值"""
        # 整数直接作为索引处理
        if isinstance(part, int):
            parent[part] = value
            return
        
        # 尝试将字符串部分解析为整数索引
        try:
            index = int(part)
            parent[index] = value
            return
        except (ValueError, TypeError):
            pass  # 不是整数索引
        
        # 尝试作为字典键设置
        if isinstance(parent, dict):
            parent[part] = value
            return
        
        # 作为对象属性设置
        setattr(parent, part, value)
