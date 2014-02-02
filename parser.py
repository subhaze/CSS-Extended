import sublime, sublime_plugin, os, re

ST2 = int(sublime.version()) < 3000
scratch_view = None
cssStyleCompletion = None

if ST2:
    import cache
    import settings
else:
    from . import cache
    from . import settings


def init_file_loading(csc):
    global cssStyleCompletion
    cssStyleCompletion = csc

    if not sublime.active_window():
        sublime.set_timeout(lambda: init_file_loading(), 500)
    else:
        load_external_files(get_external_files())


def create_output_panel(name):
    '''
        Used for loading in files outside of project view
    '''
    if ST2:
        return sublime.active_window().get_output_panel(name)
    else:
        return sublime.active_window().create_output_panel(name)


def get_external_files():
    import glob

    external_files = []
    for file_path in settings.get('load_external_files', []):
        external_files.extend(glob.glob(file_path))
    return external_files


def load_external_files(file_list, as_scratch=True):
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
        global scratch_view, cssStyleCompletion
        print('PARSING FILE', file_path)
        file_extension = os.path.splitext(file_path)[1][1:]
        if not file_extension in syntax_file:
            return
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
                    {"content": f.read()}
                )
                cache.save_cache(scratch_view, cssStyleCompletion)
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


class CssExtendedCompletionsFileCommand(sublime_plugin.TextCommand):
    global scratch_view

    def run(self, edit, content):
        # add space between any )} chars
        # ST3 throws an error in some LESS files that do this
        content = re.sub(r'\)\}', r') }', content)
        scratch_view.erase(edit, sublime.Region(0, scratch_view.size()))
        scratch_view.insert(edit, 0, content)
