from __future__ import print_function
import time
import sys

# from pathos.pools import ProcessPool as Pool
# from pathos.pools import ThreadPool as Pool
from pathos.pools import ParallelPool as Pool

def busy_add(x,y, delay=0.01):
    for n in range(x):
       x += n
    for n in range(y):
       y -= n
    time.sleep(delay)
    return x + y

def busy_squared(x):
    import random
    time.sleep(0.01*random.random())
    return x*x

def squared(x):
    return x*x

def quad_factory(a=1, b=1, c=0):
    def quad(x):
        return a*x**2 + b*x + c
    return quad

square_plus_one = quad_factory(2,0,1)

 
def test_ready(pool, f, maxtries, delay):
    print(pool)
    print("y = %s(x1,x2)" % f.__name__)
    print("x1 = %s" % str(x[:10]))
    print("x2 = %s" % str(x[:10]))
    print("I'm sleepy...")
    args = (getattr(f,'__code__',None) or getattr(f,'func_code')).co_argcount
    kwds = getattr(f,'__defaults__',None) or getattr(f,'func_defaults')
    args = args - len(kwds) if kwds else args
    if args == 1:
        m = pool.amap(f, x)
    elif args == 2:
        m = pool.amap(f, x, x)
    else:
        msg = 'takes a function of 1 or 2 required arguments, %s given' % args
        raise NotImplementedError(msg)

    tries = 0
    while not m.ready():
        if not tries: print("Z", end='')
        time.sleep(delay)
        tries += 1
        if (tries % (len(x)*0.01)) == 0:
            print('z', end='')
            sys.stdout.flush()
        if tries >= maxtries:
            print("TIMEOUT")
            break
    print("")
    y = m.get()
    print("I'm awake")
    print("y = %s" % str(y[:10]))



if __name__ == '__main__':
    x = list(range(500))
    delay = 0.01
    maxtries = 200
    f = busy_add
   #f = busy_squared
   #f = squared

   
   #from pathos.helpers import freeze_support
   #freeze_support()

    pool = Pool(nodes=4)
    test_ready( pool, f, maxtries, delay )


# import time
# from pathos.serial import SerialPool as serial
# from pathos.parallel import ParallelPool as pppool
# from pathos.multiprocessing import ProcessPool as mppool
# from timeit import Timer
# from functools import partial

# count_from = [40000000, 30000000, 20000000, 10000000]

# def countdown(n):
#     start = time.time()
#     while n > 0:
#         n -= 1
#     return time.time() - start

# def optimize(solver, model, mapper, nodes):
#     results = mapper(nodes).map(solver, model)

#     return results


# def bench(mapper, nodes):
#     t = Timer(partial(optimize, countdown, count_from, mapper, nodes))
#     print("%.2f ms/1000 ops" % (1000000 * t.timeit(number=100000)/100000))

# if __name__ == '__main__':
        
#     bench(serial, 2)
#     bench(mppool, 2)
#     bench(pppool, 2)
   
