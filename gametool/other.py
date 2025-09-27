import time
from typing import List, Dict, Tuple, Callable, Any


class IDPool:
    """ID池类，用于生成唯一的ID"""
    
    def __init__(self) -> None:
        """初始化ID池"""
        self.id = 1
        self.free_ids: set[int] = set()  # 存储未使用的ID
        self.objects: Dict[int, Any] = {}
    
    def get_id(self, obj) -> int:
        """获取一个未使用的唯一ID
        
        Returns:
            一个唯一的ID
        """
        if self.free_ids:
            # 如果有空闲ID，直接从中获取
            id_ = self.free_ids.pop()
        else:
            # 如果没有空闲ID，生成新的ID
            id_ = self.id
            self.id += 1
            self.objects[id_] = obj
        return id_
    
    def release_id(self, id_: int) -> None:
        """释放一个ID，使其可以被重新使用
        
        Args:
            id_: 要释放的ID
            
        Note:
            如果ID已经被释放，则不会重复添加
        """
        if id_ < self.id:
            self.free_ids.add(id_)  # 将ID添加到空闲ID集合中
            del self.objects[id_]
