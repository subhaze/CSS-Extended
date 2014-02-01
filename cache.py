import sublime, os, json

ST2 = int(sublime.version()) < 3000

if ST2:
    import commands
    import settings
else:
    from . import commands
    from . import settings

_file_path = None


def get_cache_path():
    global _file_path, ST2
    if _file_path:
        return _file_path

    cache_end_point = ['CSS', 'CSS.completions.cache']
    if ST2:
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
    if not settings.get('save_cache_to_file'):
        return {}
    try:
        with open(get_cache_path(), 'r') as json_data:
            return json.loads(json_data.read())
    except:
        return {}


def save_cache(view, cssStyleCompletion):
    file_key, project_key = cssStyleCompletion.getProjectKeysOfView(view)
    # if there is no project_key set the project_key as the file_key
    # so that we can cache on a per file basis
    if not project_key:
        project_key = file_key
    if project_key in cssStyleCompletion.projects_cache:
        cache = cssStyleCompletion.projects_cache[project_key]
    else:
        cache = {}

    for symbol in commands.symbol_dict:
        if '_command' in symbol:
            continue
        if symbol not in cache:
            cache[symbol] = {}
        completions = cssStyleCompletion.get_view_completions(view, symbol)
        if completions:
            cache[symbol][file_key] = completions
        elif not cache[symbol]:
            cache.pop(symbol, None)
    if cache:
        cssStyleCompletion.projects_cache[project_key] = cache
    if settings.get('save_cache_to_file'):
        # save data to disk
        json_data = open(cssStyleCompletion.cache_path, 'w')
        json_data.write(json.dumps(cssStyleCompletion.projects_cache))
        json_data.close()
