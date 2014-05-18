import sublime, os

ST2 = int(sublime.version()) < 3000

if ST2:
    import cache
    import settings
    import commands
    import project
else:
    from . import cache
    from . import settings
    from . import commands
    from . import project


def returnPseudoCompletions():
    pseudo_selector_list = settings.get("pseudo_selector_list")
    return [
        (selector + '\t pseudo selector', selector)
        for selector in pseudo_selector_list
    ]


def returnElementCompletions():
    element_list = settings.get("element_list")
    return [
        (elem + '\t element', elem)
        for elem in element_list
    ]


def returnSymbolCompletions(view, symbol_type):
    projects_cache = cache.projects_cache
    if not symbol_type in commands.symbol_dict:
        return []
    file_key, project_key = cache.get_keys(
        view,
        return_both=True
    )
    completion_list = []

    for file in project.get_external_files():
        if file in projects_cache:
            completion_list = completion_list + projects_cache[file][symbol_type][file]
    if file_key in projects_cache:
        if symbol_type in projects_cache[file_key]:
            completion_list = completion_list + projects_cache[file_key][symbol_type][file_key]
    if project_key in projects_cache:
        if symbol_type in projects_cache[project_key]:
            for file in projects_cache[project_key][symbol_type]:
                completion_list = completion_list + projects_cache[project_key][symbol_type][file]
    if completion_list:
        return [
            tuple(completions)
            for completions in completion_list
        ]
    else:
        # we have no cache so just return whats in the current view
        return get_view_completions(
            view, commands.symbol_dict[symbol_type]
        )


def get_view_completions(view, symbol_type):
    if not symbol_type in commands.symbol_dict:
        return []

    # get filename with extension
    try:
        file_name = os.path.basename(view.file_name())
    except:
        file_name = os.path.basename(view.name())
    symbols = view.find_by_selector(commands.symbol_dict[symbol_type])
    results = []
    for point in symbols:
        completion = commands.symbol_dict[symbol_type+'_command'](view, point, file_name)
        if completion is not None:
            results.extend(completion)
    return list(set(results))


def _returnViewCompletions(view):
    results = []
    for view in sublime.active_window().views():
        results += get_view_completions(view, 'class')
    return list(set(results))
