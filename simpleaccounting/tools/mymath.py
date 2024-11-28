"""
    Copyright 2024- ZiJian Jiang @ https://github.com/CallmeNezha

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from decimal import Decimal, ROUND_HALF_UP


class FloatWithPrecision:
    def __init__(self, value=0.0, precision=2):
        if isinstance(value, FloatWithPrecision):
            self.precision = value.precision
            self.value = value.value
        else:
            self.precision = precision
            self.value = self._round(value)

    def _round(self, value):
        # 将浮点数转换为 Decimal 并四舍五入到指定精度
        return float(Decimal(str(value)).quantize(Decimal("0." + "0" * self.precision), rounding=ROUND_HALF_UP))

    def __gt__(self, other):
        if isinstance(other, FloatWithPrecision):
            return self.value > other.value
        return self.value > other

    def __lt__(self, other):
        if isinstance(other, FloatWithPrecision):
            return self.value < other.value
        return self.value < other

    def __ge__(self, other):
        if isinstance(other, FloatWithPrecision):
            return self.value >= other.value
        return self.value >= other

    def __le__(self, other):
        if isinstance(other, FloatWithPrecision):
            return self.value <= other.value
        return self.value <= other

    def __abs__(self):
        return FloatWithPrecision(abs(self.value), self.precision)

    def __neg__(self):
        return FloatWithPrecision(-self.value, self.precision)

    def __add__(self, other):
        if isinstance(other, FloatWithPrecision):
            return FloatWithPrecision(self.value + other.value, self.precision)
        return FloatWithPrecision(self.value + other, self.precision)

    def __sub__(self, other):
        if isinstance(other, FloatWithPrecision):
            return FloatWithPrecision(self.value - other.value, self.precision)
        return FloatWithPrecision(self.value - other, self.precision)

    def __mul__(self, other):
        if isinstance(other, FloatWithPrecision):
            return FloatWithPrecision(self.value * other.value, self.precision)
        return FloatWithPrecision(self.value * other, self.precision)

    def __truediv__(self, other):
        if isinstance(other, FloatWithPrecision):
            return FloatWithPrecision(self.value / other.value, self.precision)
        return FloatWithPrecision(self.value / other, self.precision)

    def __eq__(self, other):
        if isinstance(other, (float, int)):
            return self.value == other
        elif isinstance(other, FloatWithPrecision):
            return self.value == other.value
        else:
            return False

    def __str__(self):
        # 将数值转换为字符串并在每三位数加逗号
        formatted_value = f"{self.value:,.{self.precision}f}"
        return formatted_value

    def __repr__(self):
        formatted_value = f"<FloatWithPrecision {self.value:,.{self.precision}f}>"
        return formatted_value

    @classmethod
    def from_string(cls, value_str, precision = 2):
        # 从带逗号的字符串转换为 FloatWithPrecision 实例
        value_str = value_str.strip().replace(',', '')
        return cls(float(value_str), precision)
