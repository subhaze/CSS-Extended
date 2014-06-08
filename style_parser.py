import sublime, sublime_plugin, os, re

ST2 = int(sublime.version()) < 3000
scratch_view = None

if ST2:
    import cache
    import commands
    import completions
    import settings
    import project
else:
    from . import cache
    from . import commands
    from . import completions
    from . import settings
    from . import project


def init_file_loading():
    if not sublime.active_window():
        sublime.set_timeout(lambda: init_file_loading(), 500)
    else:
        load_files(project.get_external_files())


def create_output_panel(name):
    '''
        Used for loading in files outside of project view
    '''
    if ST2:
        return sublime.active_window().get_output_panel(name)
    else:
        return sublime.active_window().create_output_panel(name)


def _find_file(name, path):
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
    return result


def load_linked_files(view):
    html_scope = settings.get('emmet_scope', '')
    if settings.get('index_linked_style_sheets', True) and view.score_selector(0, html_scope):
        import ntpath
        files = []
        links = []
        # regex should find, html|jade|haml style links
        view.find_all(r'(<link|link\s*\(?\{?).*href\s*(=|=>)\s*("|\')(.*?)("|\')', 0, r'$4', links)
        for path in view.window().folders():
            for css_path in links:
                files.extend(_find_file(ntpath.basename(css_path), path))
        print('Found styles linked in HTML')
        print(files)
        load_files(files, as_scratch=False)


def load_files(file_list, as_scratch=True):
    global scratch_view
    syntax_file = {
        'css': 'Packages/CSS/CSS.tmLanguage',
        'less': 'Packages/LESS/LESS.tmLanguage',
        'scss': 'Packages/SCSS/SCSS.tmLanguage'
    }

    scratch_view = create_output_panel('CSS Extended Completions')
    scratch_view.set_scratch(as_scratch)
    # sort file list by extension to reduce the frequency
    # of syntax file loads
    sorted(file_list, key=lambda x: x.split(".")[-1])
    current_syntax = {
        'isThis': ''
    }
    file_count = len(file_list)

    def parse_file(file_path, indx):
        global scratch_view
        file_extension = os.path.splitext(file_path)[1][1:]

        # Check if we have a syntax file
        if not file_extension in syntax_file:
            return
        # Check if we match CSS extensions listed
        if not file_path.endswith(tuple(settings.get('css_extension', ()))):
            return

        print('PARSING FILE', file_path)
        if not syntax_file[file_extension] == current_syntax['isThis']:
            scratch_view.set_syntax_file(syntax_file[file_extension])
            current_syntax['isThis'] = syntax_file[file_extension]
        sublime.status_message(
            'CSS Extended: parsing file %s of %s' % (indx + 1, file_count)
        )
        try:
            scratch_view.set_name(file_path)
            with open(file_path, 'r') as f:
                sublime.active_window().run_command(
                    'css_extended_completions_file',
                    # add a newlines to prevent ST3 from bailing on scope
                    # creations due to long one-line minified files
                    {"content": re.sub("{", "{\n", f.read())}
                )
                update_cache(scratch_view)
        except IOError:
            pass

    parse_delay = 0
    for indx, file_path in enumerate(file_list):
        if not os.path.isfile(file_path):
            continue
        sublime.set_timeout(
            lambda file_path=file_path, indx=indx: parse_file(file_path, indx),
            parse_delay
        )
        parse_delay = parse_delay + 250


def parse_view(view):
    global scratch_view
    file_path = view.file_name()

    # Check if we match CSS extensions listed
    if not file_path.endswith(tuple(settings.get('css_extension', ()))):
        return

    print('PARSING SAVED VIEW')
    scratch_view.set_syntax_file(view.settings().get('syntax'))
    try:
        scratch_view.set_name(file_path)
        with open(file_path, 'r') as f:
            sublime.active_window().run_command(
                'css_extended_completions_file',
                # add a newlines to prevent ST3 from bailing on scope
                # creations due to long one-line minified files
                {"content": re.sub("{", "{\n", f.read())}
            )
            update_cache(scratch_view)
    except IOError:
        pass


def update_cache(view):
    projects_cache = cache.projects_cache
    file_key, project_key = cache.get_keys(view)
    # if there is no project_key set the project_key as the file_key
    # so that we can cache on a per file basis
    if not project_key:
        project_key = file_key
    if project_key in projects_cache:
        _cache = projects_cache[project_key]
    else:
        _cache = {}

    for symbol in commands.symbol_dict:
        if '_command' in symbol:
            continue
        if symbol not in _cache:
            _cache[symbol] = {}
        _completions = completions.get_view_completions(view, symbol)
        if _completions:
            _cache[symbol][file_key] = _completions
        elif not _cache[symbol]:
            _cache.pop(symbol, None)
    if _cache:
        projects_cache[project_key] = _cache
        cache.save_cache()


class CssExtendedCompletionsFileCommand(sublime_plugin.TextCommand):
    global scratch_view

    def run(self, edit, content):
        # add space between any )} chars
        # ST3 throws an error in some LESS files that do this
        content = re.sub(r'\)\}', r') }', content)
        scratch_view.erase(edit, sublime.Region(0, scratch_view.size()))
        scratch_view.insert(edit, 0, content)
