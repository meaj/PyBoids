"""
Pyboids - Vector
 * A class containing the definitions of the Vector objects, which are two dimensional and three dimensional
 * Copyright (c) 2019 Meaj
"""
import math


class Vector2D:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    # Addition and subtraction, since you cannot add a scalar to a vector, no type checking is needed
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __rsub__(self, other):
        return self.__sub__(other)

    # Multiplication and division, we type check to account for scalar and vector multiplication
    def __mul__(self, other):
        if type(other) == Vector2D:
            return self.x * other.x + self.y * other.y
        elif type(other) == int or type(other) == float:
            return Vector2D(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if type(other) == Vector2D:
            return self.x / other.x + self.y / other.y
        elif type(other) == float or type(other) == int:
            return Vector2D(self.x / other, self.y / other)

    def __rtruediv__(self, other):
        if type(other) == Vector2D:
            return other.x / self.x + other.y / self.y
        elif type(other) == float or type(other) == int:
            return Vector2D(other / self.x, other / self.y)

    # Magnitude of the vector
    def __abs__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    # Equality operators
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    # 2D Vector printing using the default "0.0, 0.0"
    def __str__(self):
        return '{}, {}'.format(self.x, self.y)

    def normalize(self):
        mag = self.__abs__()
        if mag > 0:
            return self.__truediv__(mag)

    # Returns the direction in degrees from the y axis
    def get_direction(self):
        return math.atan2(self.x, self.y) * 180/math.pi
