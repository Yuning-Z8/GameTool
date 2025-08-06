# GameTool
一个轻量级的控制台应用程序框架，提供用户界面构建、输入处理和设置管理功能，使控制台应用程序的开发更加简单和高效。


## 功能特点
- 灵活的控制台UI构建系统，支持文本格式化、居中、对齐等功能
- 多种输入处理函数，包括带指令控制的输入和范围限制的整数输入
- 强大的设置管理系统，支持不同类型的配置项和嵌套设置菜单
- 链式调用API，使代码更加简洁和易读
- 全角字符支持，正确处理中文等全角字符的显示宽度
- 物理量格式化功能，支持距离、体积、质量和时间的自动单位转换与显示
- 数字转换功能，支持阿拉伯数字到罗马数字、英文数字和中文单位数字的转换


## 安装与使用
### 安装
该框架可以直接通过复制源代码文件使用，不需要额外安装


### 快速开始
下面是一个简单的示例，展示如何使用该框架构建一个简单的控制台应用程序：
```python
import sys

import basic
from ui import UI
from input import yinput, intinput, getname
from setting import *

basic.namespace = globals()
basic.input_act['exit'] = sys.exit

# 获取玩家名称
name = getname(1)

opt1 = Ochoice('basic', [(MD, 'font')], 'font', ['', 'vivo', 'mi', 'samsung'])
@opt1.register_condition()
def cdt1():
    return not basic.is_equal_width_font

opt2 = Ostr('名字', limit=(1, 16))
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
print(ui.flush())
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

progress = bar(75, 100, length=20)
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
`getname` 是用于获取玩家昵称的工具，支持长度验证、快捷输入、黑名单检查和重复检查：

```python
from input import getname

# 基本使用
name1 = getname(1)  # 获取玩家1的昵称
name2 = getname(2)  # 获取玩家2的昵称

# 自定义配置
getname.is_seam_name_allowed = True  # 允许重复昵称
getname.lenth_limit = (2, 15)  # 修改长度限制
getname.blacklist = ['#', '@', '!']  # 修改禁止使用的字符
getname.fast_name['ex'] = 'excemple'  # 添加快捷名称映射

# 示例
getname.is_seam_name_allowed = True  # 允许重复
player1 = getname(1)  # 提示"玩家1 请输入昵称！"
player2 = getname(2)  # 若输入与player1相同的昵称，会自动添加#1后缀
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

### 路径解析机制
GameTool 使用特殊的路径表示法来引用变量和对象，支持三种类型的路径元素：
- `CL`: 类属性
- `MD`: 模块属性
- `DL`: 字典/列表/元组元素（用于访问容器类型的元素）

使用`(类型, 键)`列表表示路径

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


## number 模块详细用法
### 物理量格式化
支持距离、体积、质量和时间的单位自动转换与显示，通过不同函数处理不同物理量，可指定初始单位和显示的单位数量。
```python
from number import auto_distance_expression, auto_volume_expression, auto_mass_expression, auto_time_expression

# 距离格式化
distance = auto_distance_expression(1500)  # 输入距离值，默认单位为米
print(distance)

# 体积格式化
volume = auto_volume_expression(5)  # 输入体积值，默认单位为立方米
print(volume)

# 质量格式化
mass = auto_mass_expression(500)  # 输入质量值，默认单位为克
print(mass)

# 时间格式化
time = auto_time_expression(30)  # 输入时间值，默认单位为秒
print(time)
```


### 添加更多物理量支持
```python
return format_physical_quantity(
    value,                # 原始数值
    val_unit,             # 原始单位
    units,                # 多语言单位名称映射
    unit_map,             # 单位层级关系（从小到大）
    conversion_factors,   # 单位换算系数（相对于基准单位）
    display_thresholds,   # 单位切换阈值
    depth                 # 显示深度
)
```

#### 单位名称映射 (`units`)
```python
units = {
    'en': ['m', 'km', 'AU', 'ly'],          # 英文单位
    'zh1': ['米', '千米', '天文单位', '光年'], # 中文单位1
    'zh2': ['米', '千米', '天文单位', '光年']  # 中文单位2
}
```
需为每种语言提供单位名称列表，顺序与 `unit_map` 一致。

#### 单位层级 (`unit_map`)
```python
unit_map = ['m', 'km', 'au', 'ly']  # 从最小单位到最大单位
```
定义单位的层级关系。

#### 单位换算系数 (`conversion_factors`)
```python
conversion_factors = {
    'm': 1,         # 1 米 = 1 米（基准单位）
    'km': 1000,      # 1 千米 = 1000 米
    'au': 15e10,     # 1 天文单位 ≈ 1.5亿公里
    'ly': 946e13     # 1 光年 ≈ 9.46万亿公里
}
```
- 所有单位需转换为基准单位（如距离以 `m` 为基准）。

#### 显示阈值 (`display_thresholds`)
用于控制单位切换的阈值和数值显示的小数位数。它的设计直接影响物理量的格式化输出结果。
```python
display_thresholds = {
    'm': [3000],        # >3000米时切换到千米
    'km': [15e8],       # >15亿米时切换到天文单位
    'au': [437e13, ...],# 天文单位的小数位控制
    'ly': [float('inf')]# 光年为最大单位
}
```

`display_thresholds` 的结构为：
```python
display_thresholds = {
    '单位1': [阈值1, 小数位数阈值1, 小数位数阈值2, ...],
    '单位2': [阈值2, ...],
    ...
}
```
函数会从最小单位开始检查，计算 `value`（换算为基准单位后的值）是否超过当前单位的 `阈值[0]`：
- 如果不超过，则使用该单位。
- 如果超过，则检查下一个更大的单位。

每个单位的 `display_thresholds` 列表可以包含 多个阈值，用于动态调整小数位数：
```python
display_thresholds = {
    'au': [1e12, 1000, 100],  # 天文单位的阈值配置
}
```  
函数会从右往左检查 `value` 是否超过这些阈值，决定保留几位小数。
- 如果 `value > 阈值[i]`，则保留 `i` 位小数。
- 如果所有阈值均不满足，则保留 `0` 位小数（整数）。

`float('inf')`：表示该单位是 最大单位，不会切换到更大的单位。  
`-1` 或 `0`：可用于强制保留小数位数。  
最后一个单位应当为`[float('inf'), ..., -1]`

### 复合单位逻辑（`depth > 1`）
当 `depth > 1` 时，函数会：
- 不同depth下的最大单位一致
- 忽略值为0的单位（除非所有单位均为0）。
- 必要时会降低depth

### 数字转换
支持阿拉伯数字到罗马数字、英文数字和中文单位数字的转换。
```python
from number import roman_numerals, english_numerals, chniese_numerals

# 阿拉伯数字转罗马数字
roman = roman_numerals(1)
print(roman)

# 阿拉伯数字转英文数字
english = english_numerals(1000)
print(english)

# 阿拉伯数字转中文单位数字
chinese = chniese_numerals(10000)
print(chinese)
```

## 许可证
GPL-3.0
