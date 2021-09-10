import sys
sys.path.insert(0, '..')
from ztrace import ztrace


@ztrace(['t', 'res'])
def trace_with_ignoring(t):
    res = 0
    for i in range(t):
        res += i # ztrace: ignore
    res *= 2
    
    res = '' # ztrace: ignore
    for i in range(t):
        res += str(i)
    res *= 2
        

trace_with_ignoring(3)
