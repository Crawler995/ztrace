from .utils import ensure_dir, save_obj


class DataCenter:
    def __init__(self, data_save_path):
        self._data = {}
        self._data_save_path = data_save_path
        
        ensure_dir(data_save_path)
        
    def submit_data(self, data_key, data_value):
        if data_key not in self._data.keys():
            self._data[data_key] = []
        self._data[data_key] += [data_value]
        
        self.export_data(self._data_save_path)
    
    def export_data(self, data_save_path):
        save_obj(self._data, data_save_path)
