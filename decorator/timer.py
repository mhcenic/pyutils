import time

def decorator(function):
    def wew(*args, **kwargs):
        start = time.time()
        x = function(*args, **kwargs)
        end = time.time()
        print(function.__name__, "execution time", end - start, "sekund.")
        return x
    return wew

@decorator
def add(a,b):
    time.sleep(1)
    return a+b

@decorator
def multiply(a,b):
    time.sleep(1)
    return a*b

print(add(2,2333452))
print(multiply(24,38))