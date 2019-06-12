import math


class Vector2D:
    def __init__(self, val_x=0.0, val_y=0.0):
        self.x = val_x
        self.y = val_y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if type(other) == Vector2D:
            return self.x * other.x + self.y * other.y
        elif type(other) == float or type(other) == int:
            return Vector2D(self.x * other, self.y * other)

    def __truediv__(self, other):
        if type(other) == Vector2D:
            return self.x / other.x + self.y / other.y
        elif type(other) == float or type(other) == int:
            return Vector2D(self.x / other, self.y / other)

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return '{}, {}'.format(self.x, self.y)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            print("Index out of range")

    def prox(self):
        return self.x ** 2 + self.y ** 2

    def argument(self):
        arg = math.degrees(math.acos(Vector2D(0, 1)*self/self.__abs__()))
        if self.x < 0:
            return 360 - arg
        else:
            return arg

