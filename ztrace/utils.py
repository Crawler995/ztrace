import json
import torch
import numpy as np
import re
import os
import time


class ExtEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, torch.Tensor):
            return o.tolist()
        
        elif isinstance(o, np.integer):
            return int(o)
        elif isinstance(o, np.floating):
            return float(o)
        elif isinstance(o, np.ndarray):
            return o.tolist()

        else:
            return super().default(o)


def save_obj(obj, p):
    with open(p, 'w') as f:
        f.write(json.dumps(obj, cls=ExtEncoder, indent=2))
        
        
def ensure_dir(p):
    if not os.path.isdir(p):
        p = os.path.dirname(p)

    if not os.path.exists(p):
        os.makedirs(p)


def get_cur_time_str():
    return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


source_cache = {}
ipython_filename_pattern = re.compile('^<ipython-input-([0-9]+)-.*>$')


def get_source_from_frame(frame):
    globs = frame.f_globals or {}
    module_name = globs.get('__name__')
    file_name = frame.f_code.co_filename
    cache_key = (module_name, file_name)
    
    if cache_key in source_cache.keys():
        return source_cache[cache_key]
    
    loader = globs.get('__loader__')

    source = None
    if hasattr(loader, 'get_source'):
        try:
            source = loader.get_source(module_name)
        except ImportError:
            pass
        if source is not None:
            source = source.splitlines()
            
    if source is None:
        ipython_filename_match = ipython_filename_pattern.match(file_name)
        if ipython_filename_match:
            entry_number = int(ipython_filename_match.group(1))
            try:
                import IPython
                ipython_shell = IPython.get_ipython()
                ((_, _, source_chunk),) = ipython_shell.history_manager. \
                                  get_range(0, entry_number, entry_number + 1)
                source = source_chunk.splitlines()
            except Exception:
                pass
        else:
            try:
                with open(file_name, 'rb') as fp:
                    source = fp.read().splitlines()
            except  (
                IOError,
                OSError,
                ValueError
            ):
                pass
            
    if source is None:
        return None

    # If we just read the source from a file, or if the loader did not
    # apply tokenize.detect_encoding to decode the source into a
    # string, then we should do that ourselves.
    if isinstance(source[0], bytes):
        encoding = 'utf-8'
        for line in source[:2]:
            # File coding may be specified. Match pattern from PEP-263
            # (https://www.python.org/dev/peps/pep-0263/)
            match = re.search(br'coding[:=]\s*([-\w.]+)', line)
            if match:
                encoding = match.group(1).decode('ascii')
                break
        source = [str(sline, encoding, 'replace') for sline in
                  source]

    source_cache[cache_key] = source
    
    return source
