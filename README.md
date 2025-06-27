# GameTool
一个轻量级的控制台应用程序框架，提供用户界面构建、输入处理和设置管理功能，使控制台应用程序的开发更加简单和高效。


## 功能特点
- 灵活的控制台UI构建系统，支持文本格式化、居中、对齐等功能
- 多种输入处理函数，包括带指令控制的输入和范围限制的整数输入
- 强大的设置管理系统，支持不同类型的配置项和嵌套设置菜单
- 链式调用API，使代码更加简洁和易读
- 全角字符支持，正确处理中文等全角字符的显示宽度


## 模块介绍
### ui 模块
提供控制台用户界面构建功能，核心是 `UI` 类，支持以下功能：
- 标题和信息文本显示
- 选项列表生成
- 分割线和居中文本
- 文本格式化和宽度计算
- 界面内容合并

### input 模块
提供增强的输入处理功能：
- `yinput(prompt)`: 带指令控制的输入函数，支持直接执行注册的命令
- `intinput(prompt, max_, min_)`: 获取指定范围内的整数输入，自动验证输入有效性

### setting 模块
提供设置管理功能，支持多种配置项类型：
- `Option`: 配置项基类
- `Oint`: 整数类型配置项
- `Obool`: 布尔类型配置项
- `Ochoice`: 多选一类型配置项
- `Ostr`: 字符串类型配置项
- `Setting`: 设置菜单类，支持嵌套菜单


## 安装与使用
### 安装
该框架可以直接通过复制源代码文件使用，不需要额外安装


### 快速开始
下面是一个简单的示例，展示如何使用该框架构建一个简单的控制台应用程序：
```python
import sys

import basic
from ui import UI
from input import yinput, intinput
from setting import *

basic.namespace = globals()
basic.input_act['exit'] = sys.exit

name = 'name'

opt1 = Ochoice('basic', [(MD, 'font')], 'font', ['', 'vivo', 'mi', 'samsung'])
@opt1.register_condition
def cdt1():
    return not basic.is_equal_width_font

opt2 = Ostr('name', limit=(1, 16))
@opt2.register_constraction
def cst1():
    return f'介绍示例, 你的名字是"{name}"'

st1 = Setting('vedio').add(
    Obool('basic', [(MD, 'is_equal_width_font')], '等宽字体'),
    opt1,
    Oint('basic', [(MD, 'ui_width')], 'UIwidth', limit=(20, 100), constraction='刷新界面生效')
)

st = Setting()

st.add(
    st1,
    opt2
)

while True:
    ui = (
        UI()
        .center('示例')
        .line('-')
        .choice(['setting', 'exit'])
    )
    i = intinput(ui.flush(), 2, 1)
    if i == 1:
        st.look()
    else:
        break

```


## UI 模块详细用法
### 创建UI实例
```python
from ui import UI

# 创建默认宽度的UI实例
ui = UI()

# 创建指定宽度的UI实例
ui = UI(width=60)
```

### 添加内容到UI
```python
# 添加标题
ui.header("游戏菜单", "0: 返回")

# 添加信息文本
ui.info("这是一个游戏菜单")

# 添加选项列表
ui.choice(["开始游戏", "加载存档", "游戏设置", "退出游戏"])

# 添加分割线
ui.line("=")

# 添加居中文本
ui.center("欢迎来到游戏世界", fillchar="*")
```

### 格式化输出
```python
# 计算文本显示宽度
from ui import display_width

text = "你好，世界！"
width = display_width(text)
print(f"文本显示宽度: {width}")

# 生成进度条
from ui import bar

progress = bar(75, 100, lenth=20)
print(f"进度: {progress} 75%")
```


## 输入模块详细用法
### 基本输入
```python
from input import yinput

# 带指令控制的输入
command = yinput("请输入命令: ")
print(f"你输入的命令是: {command}")
```

### 整数输入
```python
from input import intinput

# 获取1-10之间的整数
number = intinput("请输入1-10之间的数字: ", max_=10, min_=1)
print(f"你输入的数字是: {number}")
```


## 设置模块详细用法
### 创建配置项
```python
from setting import Oint, Obool, Ochoice, Ostr

# 整数配置项
volume = 80
opt1 = Oint(
    name="volume",
    optname="音量设置",
    constraction="设置游戏音量大小(0-100)",
    limit=(0, 100)
)

# 布尔配置项
fullscreen = True
opt2 = Obool(
    name="fullscreen",
    optname="全屏显示",
    constraction="是否使用全屏模式"
)

# 多选一配置项
difficulty = 2
opt3 = Ochoice(
    name="difficulty",
    optname="游戏难度",
    choices={
        "简单": 1,
        "中等": 2,
        "困难": 3
    },
    constraction="选择游戏难度"
)

# 字符串配置项
player_name = 'name'
opt4 = Ostr(
    name="player_name",
    optname="玩家名称",
    constraction="输入你的游戏名称",
    limit=(3, 15)
)
```

### 创建设置菜单
```python
from setting import Setting

# 创建设置菜单
game_settings = Setting("游戏设置")

# 添加配置项到菜单
game_settings.add(
    opt1,
    opt2,
    opt3,
    opt4
)

# 显示设置菜单
game_settings.look()
```

### 自定义配置项
```python
# 为配置项添加说明文本
@volume.register_constraction
def volume_constraction():
    return f"当前音量: {volume}"

# 为配置项添加显示条件
@fullscreen.register_condition
def fullscreen_condition():
    # 只有在支持全屏的系统上才显示该选项
    return system_supports_fullscreen()
``` 

### 路径
CL: class  
MD: module  
DL: dict, list, tuple  

```python
# example.py
adict = {'alist': [1, 2, 3]}
class Aclass():
    def __init__(self):
        self.astr = 'str'
```
```python
import example
import basic
from setting import Oint, Ostr
from basic import DL, CL, MD

basic.namespace = globals()

a = example.Aclass()

opt1 = Oint('example', [(MD, 'adict'), (DL, 'alist'), (DL, 1)])  # 2
opt2 = Ostr('a', [(CL, 'astr')])  # 'str'
```




## 许可证
GPL-3.0
