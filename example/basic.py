import sys
sys.path.insert(0, '..')
from ztrace import ztrace

import torch
import numpy as np


@ztrace(['t', 'res'])
def trace_basic_immutable_data(t):
    res = 0
    for i in range(t):
        res += i
    res *= 2
    
    res = ''
    for i in range(t):
        res += str(i)
    res *= 2
    
    
@ztrace(['arr', 'obj'])
def trace_basic_mutable_data(t):
    arr = []
    obj = {}
    for i in range(t):
        arr += [i]
        obj[str(i)] = i
        

@ztrace(['arr[1]', 'obj["a"]["b"]', 'cls.a'])
def trace_attr(t):
    arr = [None for _ in range(t)]
    obj = {'a': {'b': None}}
    class Cls:
        a = None
    cls = Cls()
    
    for i in range(t):
        arr[1] = i
        obj['a']['b'] = i
        cls.a = i

    
@ztrace(['arr', 'arr[1]', 'tensor', 'tensor[1]'])
def trace_special_array(t):
    arr = np.zeros((t, ))
    tensor = torch.zeros((t, ))
    
    for i in range(t):
        arr[i] = i
        tensor[i] = i
        
    tensor = torch.cat([
        tensor,
        torch.from_numpy(arr).float()
    ])
        

trace_basic_immutable_data(3)
trace_basic_immutable_data(3)
trace_basic_immutable_data(3)
trace_basic_mutable_data(3)
trace_attr(3)
trace_special_array(3)
