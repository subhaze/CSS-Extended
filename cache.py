import sublime, os

_file_path = None


def get_cache_path():
    global _file_path
    if _file_path:
        return _file_path

    cache_end_point = ['CSS', 'CSS.completions.cache']
    if int(sublime.version()) < 3000:
        _file_path = [sublime.packages_path(), '..', 'Cache'] + cache_end_point
    else:
        _file_path = [sublime.cache_path()] + cache_end_point

    _file_path = os.path.join(*_file_path)

    _file_path = os.path.abspath(_file_path)
    cache_dir = _file_path.replace('CSS.completions.cache', '')

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    return _file_path


def remove_cache():
    global _file_path
    if _file_path and os.path.isfile(_file_path):
        os.remove(_file_path)


def load():
    import json
    try:
        with open(get_cache_path(), 'r') as json_data:
            return json.loads(json_data.read())
    except:
        return {}
