import heapq
from collections import defaultdict
from typing import Callable, Dict, List, Tuple, Any

class EventManager:
    """
    事件管理器类，用于处理游戏中的即时事件和定时任务。
    支持一次性事件、周期性任务和事件订阅机制。
    """
    def __init__(self) -> None:
        self.acts: List[Callable[[], bool]] = []  # 存储游戏中的事件列表
        self.event_listeners: Dict[str, List[Tuple[Callable, bool]]] = defaultdict(list)  # 事件监听器字典，键为事件名，值为(回调函数, 是否持久)元组列表
        self.scheduled_times = []  # 使用最小堆来高效获取最早的任务
        self.scheduled_tasks: Dict[int, List[Callable[[int], int]]] = defaultdict(list)  # 使用字典存储时间戳对应的任务列表
    
    def run_cycle(self, current_time) -> None:
        """
        运行一个事件循环周期。
        
        Args:
            current_time: 当前时间戳，用于处理定时任务
        """
        self.acts = [event for event in self.acts if not event()]
        self._run_until_current_time(current_time)

    def _run_until_current_time(self, current_time):
        """
        运行所有小于等于当前时间的定时任务。
        
        Args:
            current_time: 当前时间戳
        """
        while self.scheduled_times and self.scheduled_times[0] <= current_time:
            # 获取最早的时间戳
            timestamp = heapq.heappop(self.scheduled_times)
            
            # 处理该时间戳的所有任务
            tasks = self.scheduled_tasks.pop(timestamp, [])
            for task in tasks:
                # 执行任务并获取下次执行时间
                next_time = task(timestamp)
                
                # 如果返回非零，则重新安排任务
                if next_time:
                    # 确保下次执行时间不早于当前时间戳
                    next_time = max(next_time, timestamp + 0.05)
                    self.schedule_task(next_time, task)
    
    def trigger_event(self, event_name: str, event_info = None) -> None:
        """
        触发指定事件，通知所有监听器。
        
        Args:
            event_name: 事件名称
            event_info: 事件相关信息，默认为None
        """
        if event_name in self.event_listeners:
            for monitor in self.event_listeners[event_name].copy():
                monitor[0](event_info)
                # 如果是非持久监听器，触发后移除
                if not monitor[1]:
                    self.event_listeners[event_name].remove(monitor)

    def add_act(self, func: Callable[[], bool]):
        """
        添加即时事件到事件列表。
        
        Args:
            func: 可调用对象，返回bool表示事件是否完成
        """
        self.acts.append(func)

    def schedule_task(self, timestamp: int, func: Callable[[int], int]):
        """
        添加定时任务到指定时间戳。
        
        Args:
            timestamp: 任务执行的时间戳
            func: 可调用对象，接受当前时间戳，返回下次执行时间(0表示不重复)
        """
        if timestamp not in self.scheduled_tasks:
            heapq.heappush(self.scheduled_times, timestamp)
        self.scheduled_tasks[timestamp].append(func)
    
    def subscribe(self, event_name: str, func: Callable, persist = False) -> None:
        """
        订阅指定事件。
        
        Args:
            event_name: 事件名称
            func: 事件处理函数
            persist: 是否持久订阅(False表示只触发一次)，默认为False
        """
        self.event_listeners[event_name].append((func, persist))
