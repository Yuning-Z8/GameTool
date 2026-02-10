from typing import Literal, Dict, List

from . import basic


def format_physical_quantity(value: float, value_unit: str, units: Dict[Literal['en', 'zh1', 'zh2'], List[str]], unit_map: List[str], conversion_factors: Dict[str, float], display_thresholds: Dict[str, List[float]], depth: int = 1) -> str:
    """
    格式化物理量值为合适的单位表达方式。

    根据输入的物理量值及单位，自动选择合适的单位（如 m、km、kg 等）并格式化输出。

    Args:
        value: 物理量的值
        value_unit: 物理量的单位（如 'm', 'kg', 's' 等）
        units: 不同语言下的单位名称映射
        unit_map: 单位映射列表
        conversion_factors: 单位换算比例
        display_thresholds: 单位显示的阈值配置
        depth: 显示深度（1: 单单位, 2: 双单位, 3: 三单位）

    Returns:
        格式化后的物理量字符串
    """
    value *= conversion_factors[value_unit]
    unit_ = None

    # 选择合适的单位
    for unit in display_thresholds:
        if value >= display_thresholds[unit][0]:
            continue
        unit_ = unit
        break

    if unit_ is None:
        unit_ = unit_map[-1]

    if depth == 1:
        # 确定小数位数
        thresholds = display_thresholds[unit_]
        ndigits = 0  # 默认保留0位小数

        # 从第二个阈值开始检查（第一个是单位切换阈值）
        for i in range(1, len(thresholds)):
            if value >= thresholds[i]:
                ndigits = i - 1  # 第i个阈值对应i-1位小数
                break
        else:
            # 如果没有找到满足条件的阈值，使用最大小数位数
            ndigits = len(thresholds) - 1

        # 计算转换后的值
        converted_value = value / conversion_factors[unit_]

        # 四舍五入到指定小数位数
        if ndigits == 0:
            formatted_value = round(converted_value)
        else:
            formatted_value = round(converted_value, ndigits)

        # 去掉不必要的.0
        if formatted_value.is_integer():
            formatted_value = int(formatted_value)

        return f'{formatted_value}{units[basic.unit_type][unit_map.index(unit_)]}'
    else:
        results = []
        remaining_value = value
        current_unit_idx = unit_map.index(unit_)

        for i in range(depth):
            if remaining_value == 0 or current_unit_idx < 0:
                break

            current_unit = unit_map[current_unit_idx]
            current_factor = conversion_factors[current_unit]

            # 计算当前单位的整数值
            amount = remaining_value // current_factor

            if amount > 0:
                # 直接使用整数部分
                results.append(f"{int(amount)}{units[basic.unit_type][current_unit_idx]}")
                remaining_value -= amount * current_factor
            else:
                # 对于小数部分，确定小数位数
                thresholds = display_thresholds[current_unit]
                ndigits = 0  # 默认保留0位小数

                # 从第二个阈值开始检查
                for j in range(1, len(thresholds)):
                    if remaining_value >= thresholds[j]:
                        ndigits = j - 1  # 第j个阈值对应j-1位小数
                        break
                else:
                    # 如果没有找到满足条件的阈值，使用最大小数位数
                    ndigits = len(thresholds) - 1

                # 计算并格式化小数部分
                if ndigits == 0:
                    formatted_value = round(remaining_value / current_factor)
                else:
                    formatted_value = round(remaining_value / current_factor, ndigits)

                if formatted_value.is_integer():
                    formatted_value = int(formatted_value)

                results.append(f"{formatted_value}{units[basic.unit_type][current_unit_idx]}")
                remaining_value = 0  # 小数部分处理完后，剩余值为0

            current_unit_idx -= 1

        return ' '.join(results) if results else f"0{units[basic.unit_type][unit_map.index(unit_)]}"

def auto_distance_expression(distance: float, val_unit: Literal['m', 'km', 'au', 'ly'] = 'm', depth: int = 1) -> str:
    """自动生成距离表达式

    根据距离值返回合适的单位表达方式。

    Args:
        distance: 距离值
        val_unit: 距离的初始单位（默认 m）
        depth: 显示深度（单位数量）

    Returns:
        距离的字符串表示
    """
    return format_physical_quantity(
        distance, val_unit,
        units = {
            'en': ['m', 'km', 'AU', 'ly'],
            'zh1': ['米', '千米', '天文单位', '光年'],
            'zh2': ['米', '千米', '天文单位', '光年'],
            },
        unit_map = ['m', 'km', 'au', 'ly'],
        conversion_factors = {'m': 1, 'km': 1000, 'au': 15e10, 'ly': 946e13},
        display_thresholds = {'m':[3000], 'km': [15e8], 'au': [437e13, 15e11, 15e9], 'ly': [float('inf'), float('inf'), -1]},
        depth=depth
        )

def auto_volume_expression(volume: float, val_unit: Literal['m3'] = 'm3', depth: int = 1) -> str:
    """自动生成体积表达式

    根据体积值返回合适的单位表达方式。

    Args:
        volume: 体积值
        val_unit: 体积的初始单位（默认 m3）
        depth: 显示深度（单位数量）

    Returns:
        体积的字符串表示
    """
    return format_physical_quantity(
        volume, val_unit,
        units={
            'en': ['m³'],
            'zh1': ['米³'],
            'zh2': ['立方米'],
        },
        unit_map=['m3'],
        conversion_factors={'m3': 1},
        display_thresholds={'m3': [float('inf'), 100, 10]},
        depth=depth
    )

def auto_mass_expression(mass: float, val_unit: Literal['g', 'kg', 't'] = 'g', depth: int = 1) -> str:
    """自动生成质量表达式

    根据质量值返回合适的单位表达方式。

    Args:
        mass: 质量值
        val_unit: 质量的初始单位（默认 g）
        depth: 显示深度（单位数量）

    Returns:
        质量的字符串表示
    """
    return format_physical_quantity(
        mass, val_unit,
        units={
            'en': ['g', 'kg', 't'],
            'zh1': ['克', '千克', '吨'],
            'zh2': ['克', '千克', '吨'],
        },
        unit_map=['g', 'kg', 't'],
        conversion_factors={'g': 1, 'kg': 1000, 't': 1e6},
        display_thresholds={'g': [700], 'kg': [7e5, 5000], 't': [float('inf'), 1e7, 3e6]},
        depth=depth
    )

def auto_time_expression(time: float, val_unit: Literal['s', 'min', 'h', 'd'] = 's', depth: int = 1) -> str:
    """自动生成时间表达式

    根据时间值返回合适的单位表达方式。

    Args:
        time: 时间值
        val_unit: 时间的初始单位（默认秒）
        depth: 显示深度（单位数量）

    Returns:
        时间的字符串表示
    """
    return format_physical_quantity(
        time, val_unit,
        units={
            'en': ['s', 'min', 'h', 'd'],
            'zh1': ['秒', '分钟', '小时', '天'],
            'zh2': ['秒', '分钟', '小时', '天'],
        },
        unit_map=['s', 'min', 'h', 'd'],
        conversion_factors={'s': 1, 'min': 60, 'h': 3600, 'd': 86400},
        display_thresholds={'s': [60], 'min': [3600], 'h': [86400], 'd': [float('inf')]},
        depth=depth
    )


def roman_numerals(num):
    """将阿拉伯数字转换为罗马数字

    Args:
        num: 要转换的阿拉伯数字（1-3999）

    Returns:
        对应的罗马数字字符串

    Raises:
        ValueError: 如果输入数字超出范围
    """
    if not 1 <= num <= 3999:
        raise ValueError("输入数字必须在1-3999之间")

    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

def chinese_numerals(num):
    """将阿拉伯数字转换为中文数字

    Args:
        num: 要转换的阿拉伯数字

    Returns:
        对应的中文数字字符串
    """
    if num == 0:
        return '零'
    if num < 0:
        negative = True
        num = -num
    else:
        negative = False

    units = ['', '十', '百', '千']
    units2 = ['', '万', '亿', '兆']
    digits = '零一二三四五六七八九'

    num = str(num)
    cnt = 0
    result = ''
    for i in num[::-1]:
        if cnt % 4 == 0:
            result += units2[cnt // 4]
        if i != '0':
            result += units[cnt % 4] + digits[int(i)]
        elif result and result[-1] != '零':
            result += '零'
        cnt += 1
    result = result[::-1].rstrip('零')  # 反转并去掉末尾的零
    if len(result) >= 2 and result[:2] == '一十':
        result = result[1:]
    if negative:
        result = '负' + result
    return result

def english_unit_numerals(num):
    """将阿拉伯数字转换为英文数字

    Args:
        num: 要转换的阿拉伯数字

    Returns:
        对应的英文数字字符串
    """
    units = ['', 'k', 'M', 'B', 'T']
    if num == 0:
        return '0'

    result = ''
    for i, unit in enumerate(units):
        if num % 1000 != 0:
            result = f"{num % 1000}{unit} " + result
        num //= 1000
        if num == 0:
            break
    return result.strip()

def chinese_unit_numerals(num):
    """将阿拉伯数字转换为使用中文单位数字
    Args:
        num: 要转换的阿拉伯数字
    Returns:
        对应的中文数字字符串
    """
    units = ['', '万', '亿', '兆']
    if num == 0:
        return '0'

    result = ''
    for i, unit in enumerate(units):
        if num % 10000 != 0:
            result = f"{num % 10000}{unit} " + result
        num //= 10000
        if num == 0:
            break
    return result.strip()
