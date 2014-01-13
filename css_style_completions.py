import sublime, sublime_plugin, os, json

cssStyleCompletion = None
cache_path = None
ST2 = int(sublime.version()) < 3000

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

cache_dir = cache_path.replace('CSS.completions.cache', '')

if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)


def plugin_loaded():
    global cssStyleCompletion, cache_path
    cssStyleCompletion = CssStyleCompletion(cache_path)


class CssStyleCompletion():
    def __init__(self, cache_path):
        self.cache_path = os.path.abspath(cache_path)
        self._loadCache()

    def _loadCache(self):
        try:
            json_data = open(self.cache_path, 'r')
            self.projects_cache = json.loads(json_data.read())
            json_data.close()
        except:
            self.projects_cache = {}

    def _saveCache(self, view):
        file_key, project_key = self.getProjectKeysOfView(view)
        # if there is no project_key set the project_key as the file_key
        # so that we can cache on a per file basis
        if not project_key:
            project_key = file_key
        # no cache yet
        if project_key not in self.projects_cache:
            # load up cache with all view files that are open and exit
            self.projects_cache[project_key] = self._extractCssClasses(view)

        # lazily build cache per view save
        elif project_key in self.projects_cache:
            current_cache = self.projects_cache[project_key]
            new_cache = self._extractCssClasses(view)

            # the following products a list of tuples and list
            new_cache += current_cache
            # normalize list to be a list of tuples and remove duplicates
            new_cache_set = set(tuple(item) for item in new_cache)
            # now convert to a list of list for saving.
            new_cache = [list(item) for item in new_cache_set]
            self.projects_cache[project_key][:] = new_cache
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

    def returnClassCompletions(self, view):
        file_key, project_key = self.getProjectKeysOfView(
            view,
            return_both=True
        )
        completion_list = []



        if file_key in self.projects_cache:
            completion_list = self.projects_cache[file_key]
        if project_key in self.projects_cache:
            completion_list = completion_list + self.projects_cache[project_key]


        if completion_list:
            return [ tuple(completions) for completions in completion_list]
        else:
            # we have no cache so just return whats in the current view
            return self._extractCssClasses(view)

    def _extractCssClasses(self, view):
        def genCompletionSet(symbols):
            return [(
                symbol + "\t " + file_name, symbol
            ) for symbol in symbols.split('.')[1:]]
        # get filename with extension
        file_name = os.path.basename(view.file_name())
        # TODO: allow selectors to be modified by a setting file
        symbols = view.find_by_selector('entity.other.attribute-name.class.css')
        results = []
        for point in symbols:
            results.extend(genCompletionSet(view.substr(point)))
        return list(set(results))

    def _returnViewCompletions(self, view):
        results = []
        for view in view.window().views():
            results += self._extractCssClasses(view)
        return list(set(results))

    def at_html_attribute(self, attribute, view, locations):
        selector = view.match_selector(locations[0], 'text.html string')
        if not selector:
            return False
        check_attribute = ''
        view_point = locations[0]
        char = ''
        while(char != ' ' and view_point > -1):
                char = view.substr(view_point)
                if(char != ' '):
                    check_attribute += char
                view_point -= 1
        check_attribute = check_attribute[::-1]
        if check_attribute.startswith(attribute):
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
        if cssStyleCompletion.at_html_attribute('class', view, locations):
            return (cssStyleCompletion.returnClassCompletions(view), 0)
