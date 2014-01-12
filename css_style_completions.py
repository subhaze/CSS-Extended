import sublime, sublime_plugin, os, json, sys
from collections import OrderedDict

cssStyleCompletion = None
cache_path = None

def plugin_loaded():
    global cssStyleCompletion, cache_path
    cache_path = os.path.join(sublime.cache_path(), 'CSS/CSS.completions.cache')
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
        # TODO: make this extension list a setting
        project_name = view.window().project_file_name()
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
        file_key, project_key = self.getProjectKeysOfView(view, return_both=True)
        completion_list = []
        if file_key in self.projects_cache:
            completion_list = self.projects_cache[file_key]
        if project_key in self.projects_cache:
            completion_list = completion_list + self.projects_cache[project_key]
        if completion_list:
            return completion_list
        else:
            # we have no cache so just return whats in the current view
            return self._extractCssClasses(view)

    def _extractCssClasses(self, view):
        # get filename with extension
        file_name = os.path.basename(view.file_name())
        results = [
            (view.substr(point).replace('.','') + "\t " + file_name, view.substr(point).replace('.',''))
            # TODO: allow selectors to be modified by a setting file
            for point in view.find_by_selector('entity.other.attribute-name.class.css')
        ]
        return list(set(results))

    def _returnViewCompletions(self, view):
        results = []
        for view in view.window().views():
            results += self._extractCssClasses(view)
        return list(set(results))


class CssStyleCompletionDeleteCacheCommand(sublime_plugin.WindowCommand):
    """Deletes all cache that plugin has created"""
    global cache_path, cssStyleCompletion

    def run(self):
        if cache_path:
            os.remove(cache_path)
            cssStyleCompletion.projects_cache = {}


class CssStyleCompletionEvent(sublime_plugin.EventListener):
    global cssStyleCompletion

    def on_post_save_async(self, view):
        cssStyleCompletion._saveCache(view)

    def on_query_completions(self, view, prefix, locations):
        selector = view.match_selector(locations[0], 'text.html string')
        attribute = view.expand_by_class(
            locations[0],
            sublime.CLASS_PUNCTUATION_START | sublime.CLASS_PUNCTUATION_END,
            '"\''
        )
        start = attribute.begin() - 7
        end = attribute.end()
        attribute = view.substr(sublime.Region(start, end))
        if selector and attribute.startswith('class'):
            return (cssStyleCompletion.returnClassCompletions(view), 0)
