"""
Pyboids - Vector2D
 * A class containing the definitions of the Vector2D object, which is a two dimensional vector
 * Copyright (c) 2019 Meaj
"""
import math


class Vector2D:
    def __init__(self, val_x=0.0, val_y=0.0):
        self.x = val_x
        self.y = val_y

    # 2D Vector addition
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        return self.__add__(other)

    # 2D Vector subtraction
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __rsub__(self, other):
        return self.__sub__(other)

    # 2D Vector multiplication
    def __mul__(self, other):
        if type(other) == Vector2D:
            return self.x * other.x + self.y * other.y
        elif type(other) == float or type(other) == int:
            return Vector2D(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    # 2D Vector division
    def __truediv__(self, other):
        if type(other) == Vector2D:
            return self.x / other.x + self.y / other.y
        elif type(other) == float or type(other) == int:
            if other == 0:
                other = 1
            return Vector2D(self.x / other, self.y / other)

    def __rtruediv__(self, other):
        if type(other) == Vector2D:
            return other.x / self.x + other.y / self.y
        elif type(other) == float or type(other) == int:
            return Vector2D(other / self.x, other / self.y)

    # 2D Vector's magnitude
    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    # 2D Vector equality
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    # 2D Vector printing using the default "0.0, 0.0"
    def __str__(self):
        return '{}, {}'.format(self.x, self.y)

    # Allows indexing of the vector if desired
    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            print("Index out of range")

    # Returns the angle of the vector relative to [0, 1] (straight up)
    def argument(self):
        if self.__abs__() != 0:
            arg = math.degrees(math.acos(Vector2D(0, 1)*self/self.__abs__()))
        else:
            arg = 0
        if self.x < 0:
            return 360 - arg
        else:
            return arg

