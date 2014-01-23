import sublime, sublime_plugin, os, json, re

cssStyleCompletion = None
cache_path = None
ST2 = int(sublime.version()) < 3000


def simpleCompletionSet(view, point, file_name):
    symbols = view.substr(point).strip()
    completion = [(
        symbol + "\t " + file_name, symbol
        # use the first char to split on (#|.)
    ) for symbol in symbols.split(symbols[0])[1:]]
    return completion


def scssMixinCompletionSet(view, region, file_name):
    # pattern for splitting up parameters
    re_split_params = re.compile(r',')
    end_region = view.find(r'\{', region.b)
    symbol = view.substr(region)
    symbol_snippet = view.substr(sublime.Region(region.b,end_region.a)).strip()
    # removes the parenthesis so we can template the parameters
    symbol_snippet = symbol_snippet[1:-1].strip()
    # used for displaying in the completion list
    mixin_params = re_split_params.split(symbol_snippet)
    # used for executing the completion
    mixin_params_completion = []
    if symbol_snippet:
        # if we have parameters
        # builds out the snippet for easily tabbing through parameters
        mixin_params_completion = [
            # we should end up with a string like: ${1:paramName}
            # make sure we also escape the '$' so completions expand properly
            '${%s:%s}' % (indx + 1, val.replace('$', '\\$'))
            for indx, val in enumerate(mixin_params)
        ]
    symbol_snippet_completion = '(' + ', '.join(mixin_params_completion) + ')'
    symbol_snippet = '(' + ', '.join(mixin_params) + ')'
    result = [(
        symbol + symbol_snippet + "\t " + file_name, symbol + symbol_snippet_completion + ';'
    )]
    return result


def lessMixinCompletionSet(view, region, file_name):
    # pattern for splitting up parameters
    re_split_params = re.compile(r',|;')
    # pattern to determine if the mixin symbol
    # is a definition or it's being called
    end_region = view.find(r'(?<!\@)\{|(\)\s*;)', region.b)
    # since we didn't find { assume it's a mixin being called
    # and do not parse
    if view.substr(end_region) != '{':
        return None
    # removes the leading .
    symbol = view.substr(region)[1:]
    # grabs everything from the beginning ( all the way to the {
    symbol_snippet = view.substr(sublime.Region(region.b, end_region.a))
    # make sure we remove any 'when' guards
    symbol_snippet = symbol_snippet.split('when')[0].strip()
    # removes the parenthesis so we can template the parameters
    symbol_snippet = symbol_snippet[1:-1].strip()
    # used for displaying in the completion list
    mixin_params = re_split_params.split(symbol_snippet)
    # used for executing the completion
    mixin_params_completion = []
    if symbol_snippet:
        # if we have parameters
        # builds out the snippet for easily tabbing through parameters
        mixin_params_completion = [
            # we should end up with a string like: ${1:paramName}
            '${%s:%s}' % (indx + 1, val)
            for indx, val in enumerate(mixin_params)
        ]
    symbol_snippet_completion = '(' + ', '.join(mixin_params_completion) + ')'
    symbol_snippet = '(' + ', '.join(mixin_params) + ')'
    result = [(
        symbol + symbol_snippet + "\t " + file_name, symbol + symbol_snippet_completion + ';'
    )]
    return result

symbol_dict = {
    'class': 'entity.other.attribute-name.class.css - entity.other.less.mixin',
    'id': 'entity.other.attribute-name.id.css',
    'less_var': 'variable.other.less',
    'less_mixin': 'entity.other.less.mixin',
    'scss_var': 'variable.scss',
    'scss_mixin': 'meta.at-rule.mixin.scss entity.name.function.scss',

    # Define commands for each symbol type...
    'class_command': simpleCompletionSet,
    'id_command': simpleCompletionSet,
    'less_var_command': simpleCompletionSet,
    'less_mixin_command': lessMixinCompletionSet,
    'scss_var_command': simpleCompletionSet,
    'scss_mixin_command': scssMixinCompletionSet
}

pseudo_selector_list = []

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
    global cssStyleCompletion, cache_path, settings
    cssStyleCompletion = CssStyleCompletion(cache_path)

    settings = sublime.load_settings('css_style_completions.sublime-settings')
    pseudo_selector_list = settings.get("pseudo_selector_list");

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
        global symbol_dict
        file_key, project_key = self.getProjectKeysOfView(view)
        # if there is no project_key set the project_key as the file_key
        # so that we can cache on a per file basis
        if not project_key:
            project_key = file_key
        if project_key in self.projects_cache:
            cache = self.projects_cache[project_key]
        else:
            cache = {}

        for symbol in symbol_dict:
            if '_command' in symbol:
                continue
            if symbol not in cache:
                cache[symbol] = {}
            completions = self.get_view_completions(view, symbol)
            if completions:
                cache[symbol][file_key] = completions
            elif not cache[symbol]:
                cache.pop(symbol, None)
        if cache:
            self.projects_cache[project_key] = cache

        # save data to disk
        json_data = open(self.cache_path, 'w')
        json_data.write(json.dumps(self.projects_cache))
        json_data.close()

    def getProjectKeysOfView(self, view, return_both=False):
        if not ST2:
            project_name = view.window().project_file_name()
        if ST2 or not project_name:
            # we could be ST3 but not in a true project
            # so fall back to using current folders opened within ST
            project_name = '-'.join(view.window().folders())

        css_extension = settings.get("css_extension")
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
            if symbol_type in self.projects_cache[file_key]:
                completion_list = self.projects_cache[file_key][symbol_type][file_key]
        if project_key in self.projects_cache:
            if symbol_type in self.projects_cache[project_key]:
                for file in self.projects_cache[project_key][symbol_type]:
                    completion_list = completion_list + self.projects_cache[project_key][symbol_type][file]
        if completion_list:
            return [
                tuple(completions)
                for completions in completion_list
            ]
        else:
            # we have no cache so just return whats in the current view
            return self.get_view_completions(view, symbol_dict[symbol_type])

    def get_view_completions(self, view, symbol_type):
        global symbol_dict
        if not symbol_type in symbol_dict:
            return []

        # get filename with extension
        file_name = os.path.basename(view.file_name())
        symbols = view.find_by_selector(symbol_dict[symbol_type])
        results = []
        for point in symbols:
            completion = symbol_dict[symbol_type+'_command'](view, point, file_name)
            if completion is not None:
                results.extend(completion)
        return list(set(results))

    def _returnViewCompletions(self, view):
        results = []
        for view in view.window().views():
            results += self.get_view_completions(view, 'class')
        return list(set(results))

    def at_html_attribute(self, attribute, view, locations):
        selector = view.match_selector(locations[0], settings.get("html_attribute_scope"))
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

    def at_style_symbol(self, style_symbol, style_scope, view, locations):
        selector = view.match_selector(locations[0], style_scope)
        if not selector:
            return False
        check_attribute = ''
        view_point = locations[0] - 1
        char = ''
        while(char != style_symbol and not re.match(r'[\n ]', char) and view_point > -1):
            char = view.substr(view_point)
            check_attribute += char
            view_point -= 1
        check_attribute = check_attribute[::-1]
        if check_attribute.startswith(style_symbol):
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
            return (cssStyleCompletion.returnSymbolCompletions(view, 'class'), sublime.INHIBIT_WORD_COMPLETIONS)
        if cssStyleCompletion.at_html_attribute('id', view, locations):
            return (cssStyleCompletion.returnSymbolCompletions(view, 'id'), sublime.INHIBIT_WORD_COMPLETIONS)

        # inside HTML with Emmet completions
        if settings.get("use_emmet"):
            if cssStyleCompletion.at_style_symbol('.', settings.get("emmet_scope"), view, locations):
                return (cssStyleCompletion.returnSymbolCompletions(view, 'class'), sublime.INHIBIT_WORD_COMPLETIONS)
            if cssStyleCompletion.at_style_symbol('#', settings.get("emmet_scope"), view, locations):
                return (cssStyleCompletion.returnSymbolCompletions(view, 'id'), sublime.INHIBIT_WORD_COMPLETIONS)

        # inside CSS scope pseudo completions
        if cssStyleCompletion.at_style_symbol(':', settings.get("css_completion_scope"), view, locations):
            return (cssStyleCompletion.returnPseudoCompletions(), sublime.INHIBIT_WORD_COMPLETIONS)

        # inside CSS scope symbol completions
        if cssStyleCompletion.at_style_symbol('.', settings.get("css_completion_scope"), view, locations):
            return (cssStyleCompletion.returnSymbolCompletions(view, 'class'), sublime.INHIBIT_WORD_COMPLETIONS)
        if cssStyleCompletion.at_style_symbol('#', settings.get("css_completion_scope"), view, locations):
            return (cssStyleCompletion.returnSymbolCompletions(view, 'id'), sublime.INHIBIT_WORD_COMPLETIONS)

        # inside LESS scope symbol completions
        if cssStyleCompletion.at_style_symbol(
            '@', 'source.less',
            view, locations
        ):
            return (
                cssStyleCompletion.returnSymbolCompletions(
                    view, 'less_var'
                ), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        if cssStyleCompletion.at_style_symbol(
            '.', 'source.less',
            view, locations
        ):
            return (
                cssStyleCompletion.returnSymbolCompletions(
                    view, 'less_mixin'
                ), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        # inside SCSS scope symbol completions
        if cssStyleCompletion.at_style_symbol(
            '$', 'source.scss, meta.property-value.scss',
            view, locations
        ):
            return (
                cssStyleCompletion.returnSymbolCompletions(
                    view, 'scss_var'
                ), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        if view.match_selector(
            locations[0],
            'meta.property-list.scss meta.at-rule.include.scss'
        ):
            return (
                cssStyleCompletion.returnSymbolCompletions(
                    view , 'scss_mixin'
                ), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        return None
