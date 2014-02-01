import sublime, os


def get_cache_path():
    cache_end_point = ['CSS', 'CSS.completions.cache']
    if int(sublime.version()) < 3000:
        file_path = [sublime.packages_path(), '..', 'Cache'] + cache_end_point
    else:
        file_path = [sublime.cache_path()] + cache_end_point

    file_path = os.path.join(*file_path)

    file_path = os.path.abspath(file_path)
    cache_dir = file_path.replace('CSS.completions.cache', '')

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    return file_path


def load():
    import json
    try:
        with open(get_cache_path(), 'r') as json_data:
            return json.loads(json_data.read())
    except:
        return {}
