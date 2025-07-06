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
提供控制台用户界面构建功能，核心是 `UI` 类，支持标题、选项列表、分割线等元素构建。  

### input 模块  
提供增强的输入处理功能，包括带指令控制的输入和范围限制的整数输入，以及玩家昵称获取工具。  

### setting 模块  
提供设置管理功能，支持整数、布尔、多选一、字符串等多种配置项类型，以及嵌套设置菜单。  


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
@opt1.register_condition()
def cdt1():
    return not basic.is_equal_width_font

opt2 = Ostr('name', limit=(1, 16))
@opt2.register_constraction()
def cst1():
    return f'当前名称: "{name}"'

st1 = Setting('显示设置').add(
    Obool('basic', [(MD, 'is_equal_width_font')], '等宽字体'),
    opt1,
    Oint('basic', [(MD, 'ui_width')], 'UI宽度', limit=(20, 100), constraction='刷新界面生效')
)

st = Setting()

st.add(
    st1,
    opt2
)

while True:
    ui = (
        UI()
        .center_text('示例')
        .line('-')
        .choice(['设置', '退出'])
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
ui.split_text("游戏菜单", "0: 返回")

# 添加信息文本
ui.text("这是一个游戏菜单")

# 添加选项列表
ui.choice(["开始游戏", "加载存档", "游戏设置", "退出游戏"])

# 添加分割线
ui.line("=")

# 添加居中文本
ui.center_text("欢迎来到游戏世界", fillchar="*")
```

### 输出
```python
print(ui.flush)
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
### yinput
`yinput` 支持直接执行预注册的指令，例如退出、帮助等：

```python
from input import yinput
import basic
import sys

# 注册指令：键为指令字符串，值为执行函数
basic.input_act = {
    'exit': sys.exit,  # 退出程序
    'help': lambda: print("帮助信息：输入exit退出，输入clear清屏"),
    'clear': lambda: print("\033c")  # 清屏（支持ANSI终端）
}  

# 使用示例
while True:
    cmd = yinput("请输入命令 (输入help查看帮助): ")
    if cmd not in basic.input_act:
        print(f"未知命令: {cmd}")
```

### intinput
```python
from input import intinput

# 获取1-10之间的整数
number = intinput("请输入1-10之间的数字: ", max_=10, min_=1)
print(f"你输入的数字是: {number}")
```

### getname
`getname` 是用于获取玩家昵称的工具，支持长度验证、快捷输入和重复检查：

```python
from input import getname

# 基本使用
name1 = getname(1)  # 获取玩家1的昵称
name2 = getname(2)  # 获取玩家2的昵称

# 允许重复昵称
getname.is_seam_name_allowed = True  # 默认不允许

# 示例
getname.is_seam_name_allowed = False  # 不允许重复
player1 = getname(1)  # 提示"玩家1 请输入昵称！
player2 = getname(2)  # 若输入与player1相同的昵称，会提示错误并要求重新输入
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
# 为配置项添加动态说明文本
@opt1.register_constraction()
def volume_constraction():
    return f"当前音量: {volume} (0-100)"

# 为配置项添加显示条件
@opt2.register_condition()
def fullscreen_condition():
    # 只有在支持全屏的系统上才显示该选项
    return system_supports_fullscreen() 
```


## 路径解析机制
GameTool 使用特殊的路径表示法来引用变量和对象，支持三种类型的路径元素：
- `CL`: 类属性
- `MD`: 模块属性
- `DL`: 字典/列表/元组元素（用于访问容器类型的元素）

### 路径引用示例
```python
# example.py
adict = {'alist': [1, 2, 3]}
class Aclass():
    def __init__(self):
        self.astr = '示例字符串'
```

```python
import example
import basic
from setting import Oint, Ostr
from basic import DL, CL, MD

basic.namespace = globals()

a = example.Aclass()

# 引用 example.adict['alist'][1]（值为2）
opt1 = Oint('example', [(MD, 'adict'), (DL, 'alist'), (DL, 1)])
# 引用 a.astr（值为'示例字符串'）
opt2 = Ostr('a', [(CL, 'astr')])
```


## 许可证
GPL-3.0
