import os
import sys
import time
import functools
import inspect
import re

from copy import deepcopy
from types import FrameType, FunctionType
from typing import Callable, List, Optional

from .utils import get_source_from_frame


DISABLED = bool(os.getenv('ZEXPER_DISABLED', ''))


class Tracer:
    def __init__(self, key_vars_name: List[str]):
        self._key_vars_name = key_vars_name

        self._key_vars_value_record = {key_var_name: [] for key_var_name in key_vars_name}
        self._last_vars_value = None
        self._function = None
        self._skip_next_trace = False
        
        from .manager import manager
        self._manager = manager

    def _get_data(self):
        return {
            'function_location': inspect.getfile(self._function),
            'function_name': self._function.__name__,
            'key_vars_value_record': {k: v[0] if isinstance(v, list) and len(v) == 1 else v 
                                      for k, v in self._key_vars_value_record.items()}
        }

    def __call__(self, function: FunctionType):
        if DISABLED:
            return function
        
        return self._wrap_function(function)

    def _wrap_function(self, function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            self._function = function
            self._key_vars_value_record = {key_var_name: [] for key_var_name in self._key_vars_name}
            self._last_vars_value = None
        
            sys.settrace(self._trace)
            res = function(*args, **kwargs)
            sys.settrace(None)
            
            self._manager.submit_data_record(self)

            return res
        
        return wrapper

    def _get_key_vars_value_from_frame(self, frame: FrameType):
        res = {}
        for var_name, value in frame.f_locals.items():
            if var_name in self._key_vars_name:
                res[var_name] = deepcopy(value)
                
        for i, key_var_name in enumerate(self._key_vars_name):
            if key_var_name in res.keys():
                continue
            
            main_key_var_name_regx = re.compile('(.+?)(\.|\[)')
            main_key_var_name_res = main_key_var_name_regx.findall(key_var_name)
            if len(main_key_var_name_res) == 0:
                continue
            main_key_var_name = main_key_var_name_res[0][0]
            
            rest_value_fetch_expr = key_var_name[len(main_key_var_name):]
            
            if main_key_var_name not in frame.f_locals.keys():
                continue
            
            try:
                res[key_var_name] = deepcopy(eval('frame.f_locals["{}"]{}'.format(main_key_var_name, rest_value_fetch_expr)))
            except KeyError:
                continue
            except AttributeError:
                continue
            
        return res 
    
    def _is_tracing_frame(self, frame: FrameType):
        """Only tracing the code in :attr:`self._function`. 
        The frame which is located in other functions and libraries is ignored. 
        """
        return frame.f_code.co_filename == self._function.__code__.co_filename and \
            frame.f_code.co_name == self._function.__name__

    def _trace(self, frame: FrameType, event, arg):
        if not self._is_tracing_frame(frame):
            return None
        
        cur_key_vars_value = self._get_key_vars_value_from_frame(frame)
        diff_key_vars_value = self._get_diff_vars_value(cur_key_vars_value, self._last_vars_value)
        
        if self._skip_next_trace:
            diff_key_vars_value = {}
        line_no = frame.f_lineno
        source = get_source_from_frame(frame)
        if source is None:
            self._skip_next_trace = False
        else:
            source_line = source[line_no - 1]
            self._skip_next_trace = 'ztrace: ignore' in source_line

        for key, value in diff_key_vars_value.items():
            self._key_vars_value_record[key] += [value]
        self._update_last_vars_value(cur_key_vars_value)
        
        return self._trace

    def _get_diff_vars_value(self, cur_vars_value: dict, last_vars_value: Optional[dict]):
        diff_res = {}

        if last_vars_value is None:
            return cur_vars_value

        for key, value in cur_vars_value.items():
            if key not in last_vars_value.keys():
                diff_res[key] = value
                continue
            
            if repr(value) != repr(last_vars_value[key]):
                diff_res[key] = value
        
        return diff_res

    def _update_last_vars_value(self, cur_vars_value: dict):
        if self._last_vars_value is None:
            self._last_vars_value = {}

        for key, value in cur_vars_value.items():
            self._last_vars_value[key] = deepcopy(value)
