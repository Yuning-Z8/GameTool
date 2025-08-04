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

class EventQueue:
    """事件队列类，用于管理游戏中的事件"""
    
    def __init__(self) -> None:
        """初始化事件队列"""
        self.queue: List[Tuple[int, Callable]] = []  # 存储事件的队列
    
    def add_event(self, time: int, event: Callable) -> None:
        """添加一个新的事件到队列
        
        Args:
            time: 事件发生的时间
            event: 事件处理函数
        """
        self.queue.append((time, event))
        self.queue.sort(key=lambda x: x[0])  # 按时间排序
    
    def run(self) -> None:
        """处理当前时间之前的所有事件
        
        Args:
            current_time: 当前游戏时间
        """
        current_time = int(time.time())
        while self.queue and self.queue[0][0] <= current_time:
            _, event = self.queue.pop(0)  # 获取并移除最早的事件
            event()  # 执行事件处理函数

class Events:
    def __init__(self) -> None:
        self.events: List[Callable[[], bool]] = []  # 存储游戏中的事件列表
    
    def run(self) -> None:
        for event in self.events:
            if event():
                self.events.remove(event)
