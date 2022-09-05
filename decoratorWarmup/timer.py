import time 

def printTime(func):
    def inner(*args, **kwargs):
        print("Time of execution of decorated function is:", func(*args, **kwargs))
    return inner

def timer(func):
    def inner(*args, **kwargs): 
        timeStart = time.time()
        func(*args, **kwargs)
        timeStop = time.time()
        return timeStop-timeStart
    return inner

@printTime
@timer
def longLoop(lengthOfLoop):
    sumOfElements = 0
    for i in range(lengthOfLoop):
        sumOfElements += 1
    print("Loop was executed!")

longLoop(10000000)

"""
MÓJ KOMENATRZ DO SPRAWDZENIA: 
Dodanie w przypadku funkcji dekorujących *args, **kwargs do funkcji dekorowanej, 
zapewnia niezależność od ilości zmiennych jakie potrzebuje funkcja dekorowana.
"""