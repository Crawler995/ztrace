from typing import List
from .tracer import Tracer
from .data_center import DataCenter
from .utils import get_cur_time_str


class Manager:
    def __init__(self):
        self._tracers: List[Tracer] = []
        self._data_manager: DataCenter = DataCenter(self._get_data_save_path())
        
    def _get_data_save_path(self):
        cur_time_str = get_cur_time_str()
        return './ztrace_logs/{}/{}.json'.format(cur_time_str[:8], cur_time_str[8:])
        
    def submit_data_record(self, tracer: Tracer):
        data = tracer._get_data()
        data_key = data['function_location'][:-3] + '/' + data['function_name'] + '()'
        data_value = {
            'data': data['key_vars_value_record'],
            'time': get_cur_time_str()
        }

        self._data_manager.submit_data(data_key, data_value)


manager = Manager()
