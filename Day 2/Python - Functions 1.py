def add(a, b):
    return a + b

result = add(5, 3)
print(result)   # 8

def stats(a, b):
    return a + b, a * b

s, m = stats(4, 3)
print(s, m)   # 7 12


def total(*nums):
    return sum(nums)

print(total(1, 2, 3, 4))  # 10


square = lambda x: x * x
print(square(5))  # 25


def factorial(n):
    if n == 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))  # 120


def make_multiplier(n):
    def multiply(x):
        return x * n
    return multiply

double = make_multiplier(2)
print(double(10))  # 20
