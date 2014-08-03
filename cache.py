import sublime, os, json

ST2 = int(sublime.version()) < 3000

if ST2:
    import commands
    import settings
else:
    from . import commands
    from . import settings

projects_cache = {}
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


def prune_cache():
    global projects_cache

    load()
    missing = []
    for path in projects_cache:
        if not os.path.isfile(path) and not os.path.isdir(path):
            missing.append((projects_cache, path))
        if os.path.isdir(path):
            for project in projects_cache[path]:
                # f (dict of files)
                for f in projects_cache[path][project]:
                    if not os.path.isfile(f):
                        missing.append((projects_cache[path][project],f))
    print('CSS Extended: Removing %s items from cache.' % len(missing))
    for items in missing:
        del items[0][items[1]]
    save_cache()


def remove_cache():
    global _file_path

    if _file_path and os.path.isfile(_file_path):
        os.remove(_file_path)


def load():
    global projects_cache
    if not settings.get('save_cache_to_file'):
        return
    try:
        with open(get_cache_path(), 'r') as json_data:
            projects_cache = json.loads(json_data.read())
    except:
        return


def save_cache():
    global projects_cache
    if settings.get('save_cache_to_file'):
        # save data to disk
        json_data = open(get_cache_path(), 'w')
        json_data.write(json.dumps(projects_cache))
        json_data.close()


def get_keys(view, return_both=False):
    if view.is_scratch():
        project_name = view.name()
    if not ST2:
        project_name = sublime.active_window().project_file_name()
    if ST2 or not project_name:
        # we could be ST3 but not in a true project
        # so fall back to using current folders opened within ST
        project_name = '-'.join(sublime.active_window().folders())

    css_extension = settings.get("css_extension")
    try:
        file_extension = os.path.splitext(view.file_name())[1]
    except:
        file_extension = os.path.splitext(view.name())[1]
    file_name = view.file_name()
    if not file_name:
        file_name = view.name()

    # if we have a project and we're working in a stand alone style file
    # return the project file name as the key
    if file_extension in css_extension and project_name:
        return (file_name, project_name)
    # if we are not overriding to get both keys
    # just return the file_name/file_key
    if not return_both:
        return (file_name, None)
    elif return_both and project_name:
        return (file_name, project_name)
