import sublime, sublime_plugin, os, json, re

cssStyleCompletion = None
cache_path = None
ST2 = int(sublime.version()) < 3000
symbol_dict = {
    'class': 'entity.other.attribute-name.class.css',
    'id': 'entity.other.attribute-name.id.css'
}
# TODO: eventually move this out into settings
pseudo_selector_list = [
    'after',   # should be element, but works with : currently
    'before',  # see comment above
    'checked',
    'default',
    'disabled',
    'empty',
    'enabled',
    'first',
    'first-child',
    'first-letter',  # see comment above
    'first-line',  # see comment above
    'first-of-type',
    'focus',
    'fullscreen',
    'hover',
    'indeterminate',
    'invalid',
    'lang',
    'last-child',
    'last-of-type',
    'left',
    'link',
    'not',
    'nth-child',
    'nth-last-child',
    'nth-last-type-of',
    'nth-type-of',
    'only-child',
    'only-type-of',
    'optional',
    'read-only',
    'read-write',
    'required',
    'right',
    'root',
    'scope',
    'target',
    'valid',
    'visited'
]

if ST2:
    cache_path = os.path.join(
        sublime.packages_path(),
        '..',
        'Cache',
        'CSS',
        'CSS.completions.cache'
    )
if not ST2:
    cache_path = os.path.join(
        sublime.cache_path(),
        'CSS',
        'CSS.completions.cache'
    )
cache_path = os.path.abspath(cache_path)
cache_dir = cache_path.replace('CSS.completions.cache', '')

if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)


def plugin_loaded():
    global cssStyleCompletion, cache_path
    cssStyleCompletion = CssStyleCompletion(cache_path)


class CssStyleCompletion():
    def __init__(self, cache_path):
        self.cache_path = cache_path
        self._loadCache()

    def _loadCache(self):
        try:
            json_data = open(self.cache_path, 'r')
            self.projects_cache = json.loads(json_data.read())
            json_data.close()
        except:
            self.projects_cache = {}

    def back_compat(self, cache_item):
        # TODO: remove within the next few updates
        # adding for backwards compatibility due this
        # property being used as a list before, but now
        # as a dict...
        if isinstance(cache_item, list):
            cache_item = {}
        return cache_item

    def _saveCache(self, view):
        global symbol_dict
        file_key, project_key = self.getProjectKeysOfView(view)
        # if there is no project_key set the project_key as the file_key
        # so that we can cache on a per file basis
        if not project_key:
            project_key = file_key
        # no cache yet
        if project_key not in self.projects_cache:
            # load up cache with all view files that are open and exit
            self.projects_cache[project_key] = {}
            for symbol in symbol_dict:
                self.projects_cache[project_key][symbol] = self._extractSymbol(view, symbol)

        # lazily build cache per view save
        elif project_key in self.projects_cache:
            current_cache = self.projects_cache[project_key]

            # for backward compatibility
            self.back_compat(current_cache)

            for symbol in symbol_dict:
                new_cache = self._extractSymbol(view, symbol)

                if not symbol in current_cache:
                    current_cache[symbol] = []
                # the following products a list of tuples and list
                current_cache[symbol] += new_cache
                # normalize list to be a list of tuples and remove duplicates
                new_cache_set = set(tuple(item) for item in current_cache[symbol])
                # now convert to a list of list for saving.
                current_cache[symbol] = [list(new_item) for new_item in new_cache_set]

            self.projects_cache[project_key] = current_cache
        # save data to disk
        json_data = open(self.cache_path, 'w')
        json_data.write(json.dumps(self.projects_cache))
        json_data.close()

    def getProjectKeysOfView(self, view, return_both=False):
        if ST2:
            project_name = '-'.join(view.window().folders())
        else:
            project_name = view.window().project_file_name()
        # TODO: make this extension list a setting
        css_extension = ('.css', '.less')
        file_extension = os.path.splitext(view.file_name())[1]
        file_name = view.file_name()
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

    def returnPseudoCompletions(self):
        global pseudo_selector_list
        return [(selector + '\t pseudo selector', selector) for selector in pseudo_selector_list]

    def returnSymbolCompletions(self, view, symbol_type):
        global symbol_dict
        if not symbol_type in symbol_dict:
            return []
        file_key, project_key = self.getProjectKeysOfView(
            view,
            return_both=True
        )
        completion_list = []

        if file_key in self.projects_cache:
            # for backward compatibility
            self.projects_cache[file_key] = self.back_compat(self.projects_cache[file_key])
            if symbol_type in self.projects_cache[file_key]:
                completion_list = self.projects_cache[file_key][symbol_type]
        if project_key in self.projects_cache:
            # for backward compatibility
            self.projects_cache[project_key] = self.back_compat(self.projects_cache[project_key])
            if symbol_type in self.projects_cache[project_key]:
                completion_list = completion_list + self.projects_cache[project_key][symbol_type]
        if completion_list:
            return [
                tuple(completions)
                for completions in completion_list
            ]
        else:
            # we have no cache so just return whats in the current view
            return self._extractSymbol(view, symbol_dict[symbol_type])

    def _extractSymbol(self, view, symbol_type):
        global symbol_dict

        if not symbol_type in symbol_dict:
            return []

        def genCompletionSet(symbols):
            return [(
                symbol + "\t " + file_name, symbol
            # use the first char to split on (#|.)
            ) for symbol in symbols.split(symbols[0])[1:]]

        # get filename with extension
        file_name = os.path.basename(view.file_name())
        # TODO: allow selectors to be modified by a setting file
        symbols = view.find_by_selector(symbol_dict[symbol_type])
        results = []
        for point in symbols:
            results.extend(genCompletionSet(view.substr(point)))
        return list(set(results))

    def _returnViewCompletions(self, view):
        results = []
        for view in view.window().views():
            results += self._extractSymbol(view, 'class')
        return list(set(results))

    def at_html_attribute(self, attribute, view, locations):
        selector = view.match_selector(locations[0], 'text.html string')
        if not selector:
            return False
        check_attribute = ''
        view_point = locations[0]
        char = ''
        selector_score = 1
        while((char != ' ' or selector_score != 0) and view_point > -1):
            char = view.substr(view_point)
            selector_score = view.score_selector(view_point, 'string')
            if(char != ' ' or selector_score != 0):
                check_attribute += char
            view_point -= 1
        check_attribute = check_attribute[::-1]
        if check_attribute.startswith(attribute):
                return True
        return False

    def at_css_selector(self, css_selector, view, locations):
        selector = view.match_selector(locations[0], 'meta.selector.css')
        if not selector:
            return False
        check_attribute = ''
        view_point = locations[0] - 1
        char = ''
        while(char != css_selector and not re.match(r'\n', char) and view_point > -1):
            char = view.substr(view_point)
            check_attribute += char
            view_point -= 1
        check_attribute = check_attribute[::-1]
        if check_attribute.startswith(css_selector):
            return True
        return False


if ST2:
    cssStyleCompletion = CssStyleCompletion(cache_path)


class CssStyleCompletionDeleteCacheCommand(sublime_plugin.WindowCommand):
    """Deletes all cache that plugin has created"""
    global cache_path, cssStyleCompletion

    def run(self):
        if cache_path:
            os.remove(cache_path)
            cssStyleCompletion.projects_cache = {}


class CssStyleCompletionEvent(sublime_plugin.EventListener):
    global cssStyleCompletion

    def on_post_save(self, view):
        if not ST2:
            return
        cssStyleCompletion._saveCache(view)

    def on_post_save_async(self, view):
        cssStyleCompletion._saveCache(view)

    def on_query_completions(self, view, prefix, locations):
        # inside HTML scope completions
        if cssStyleCompletion.at_html_attribute('class', view, locations):
            return (cssStyleCompletion.returnSymbolCompletions(view, 'class'), 0)
        if cssStyleCompletion.at_html_attribute('id', view, locations):
            return (cssStyleCompletion.returnSymbolCompletions(view, 'id'), 0)

        # inside CSS scope pseudo completions
        if cssStyleCompletion.at_css_selector(':', view, locations):
            print('the prefix ', prefix)
            return (cssStyleCompletion.returnPseudoCompletions(), 0)

        # inside CSS scope symbol completions
        if cssStyleCompletion.at_css_selector('.', view, locations):
            return (cssStyleCompletion.returnSymbolCompletions(view, 'class'), 0)
        if cssStyleCompletion.at_css_selector('#', view, locations):
            return (cssStyleCompletion.returnSymbolCompletions(view, 'id'), 0)

        return None
