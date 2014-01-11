import sublime, sublime_plugin, os, json

cssStyleCompletion = None


def plugin_loaded():
    global cssStyleCompletion
    cache_path = os.path.join(sublime.cache_path(), 'CSS.cache')
    cssStyleCompletion = CssStyleCompletion(cache_path)


class CssStyleCompletion():
    def __init__(self, cache_path):
        self.cache_path = cache_path
        self._loadCache()

    def _loadCache(self):
        try:
            json_data = open(self.cache_path, 'r').read()
            self.projects_cache = json.loads(json_data)
            json_data.close()
        except:
            self.projects_cache = {}

    def _saveCache(self, view):
        project_key = self.getProjectKeyOfView(view)
        # not within a project
        if not project_key: return
        # within project but no cache yet
        if project_key not in self.projects_cache:
            # load up cache with all view files that are open and exit
            self.projects_cache[project_key] = self._returnViewCompletions(view)
        # lazily build cache per view save
        elif project_key in self.projects_cache:
            current_cache = self.projects_cache[project_key]
            new_cache = self._extractCssClasses(view)
            new_cache += current_cache
            self.projects_cache[project_key][:] = list(set(new_cache))
        # save data to disk
        json_data = open(self.cache_path, 'w')
        json_data.write(json.dumps(self.projects_cache))
        json_data.close()

    def getProjectKeyOfView(self, view):
        return view.window().project_file_name()

    def returnClassCompletions(self, view):
        project_key = self.getProjectKeyOfView(view)
        if project_key and project_key in self.projects_cache:
            return self.projects_cache[project_key]
        else: return self._returnViewCompletions(view)

    def _extractCssClasses(self, view):
        results = [
            (view.substr(point).replace('.','') + "\t CSS", view.substr(point).replace('.',''))
            for point in view.find_by_selector('entity.other.attribute-name.class.css')
        ]
        return list(set(results))

    def _returnViewCompletions(self, view):
        results = []
        for view in view.window().views():
            results += self._extractCssClasses(view)
        return list(set(results))


class CssStyleCompletionEvent(sublime_plugin.EventListener):
    global cssStyleCompletion
    def on_post_save_async(self, view):
        cssStyleCompletion._saveCache(view)

    def on_query_completions(self, view, prefix, locations):
        selector = view.match_selector(locations[0], 'text.html string')
        attribute = view.expand_by_class(locations[0], sublime.CLASS_PUNCTUATION_START | sublime.CLASS_PUNCTUATION_END, '"\'')
        start = attribute.begin() - 7
        end = attribute.end()
        attribute = view.substr(sublime.Region(start, end))
        if selector and attribute.startswith('class'):
            return (cssStyleCompletion.returnClassCompletions(view), 0)
