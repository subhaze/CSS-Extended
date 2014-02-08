import sublime, sublime_plugin, os
ST2 = int(sublime.version()) < 3000

if ST2:
    # ST 2
    import commands
    import cache
    import settings
    import location
    import style_parser
else:
    # ST 3
    from . import commands
    from . import cache
    from . import settings
    from . import location
    from . import style_parser


cssStyleCompletion = None
pseudo_selector_list = []


def plugin_loaded():
    global cssStyleCompletion, pseudo_selector_list

    cssStyleCompletion = CssStyleCompletion(cache.get_cache_path())
    pseudo_selector_list = settings.get("pseudo_selector_list")
    style_parser.init_file_loading(cssStyleCompletion)


class CssStyleCompletion():
    def __init__(self, cache_path):
        self.cache_path = cache_path
        self.projects_cache = cache.load()

    def returnPseudoCompletions(self):
        global pseudo_selector_list
        return [
            (selector + '\t pseudo selector', selector)
            for selector in pseudo_selector_list
        ]

    def returnSymbolCompletions(self, view, symbol_type):
        if not symbol_type in commands.symbol_dict:
            return []
        file_key, project_key = cache.get_keys(
            view,
            return_both=True
        )
        completion_list = []

        for file in style_parser.get_external_files():
            if file in self.projects_cache:
                completion_list = completion_list + self.projects_cache[file][symbol_type][file]
        if file_key in self.projects_cache:
            if symbol_type in self.projects_cache[file_key]:
                completion_list = completion_list + self.projects_cache[file_key][symbol_type][file_key]
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
            return self.get_view_completions(
                view, commands.symbol_dict[symbol_type]
            )

    def get_view_completions(self, view, symbol_type):
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

    def _returnViewCompletions(self, view):
        results = []
        for view in sublime.active_window().views():
            results += self.get_view_completions(view, 'class')
        return list(set(results))


class CssStyleCompletionDeleteCacheCommand(sublime_plugin.WindowCommand):
    """Deletes all cache that plugin has created"""
    global cssStyleCompletion

    def run(self):
        cache.remove_cache()
        cssStyleCompletion.projects_cache = {}


class AddToCacheCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], name="", file_type="*.*"):
        import glob
        current_delay = 100
        for path in paths:
            if os.path.isdir(path):
                sublime.set_timeout(lambda: style_parser.load_external_files(
                    glob.glob(path + os.path.sep + file_type),
                    as_scratch=False
                ), current_delay)
                current_delay = current_delay + 100


class CssStyleCompletionEvent(sublime_plugin.EventListener):
    global cssStyleCompletion

    def on_post_save(self, view):
        if not ST2:
            return
        cache.save_cache(view, cssStyleCompletion)

    def on_post_save_async(self, view):
        cache.save_cache(view, cssStyleCompletion)

    def on_load(self, view):
        if settings.get('auto_trigger_emmet_completions', False):
            emmet_trigger = {'selector': 'text.html', 'characters': '.#'}
            triggers = view.settings().get('auto_complete_triggers')
            triggers.append(emmet_trigger)
            view.settings().set('auto_complete_triggers', triggers)

    def on_query_completions(self, view, prefix, locations):
        # inside HTML scope completions
        html_attr_scope = view.match_selector(
            locations[0], settings.get("html_attribute_scope")
        )

        class_attr = location.at_html_attribute('class', view, locations)
        if class_attr and html_attr_scope:
            return (
                cssStyleCompletion.returnSymbolCompletions(view, 'class'),
                sublime.INHIBIT_WORD_COMPLETIONS
            )

        id_attr = location.at_html_attribute('id', view, locations)
        if id_attr and html_attr_scope:
            return (
                cssStyleCompletion.returnSymbolCompletions(view, 'id'),
                sublime.INHIBIT_WORD_COMPLETIONS
            )

        # inside HTML with Emmet completions
        if settings.get("use_emmet"):
            if location.at_style_symbol('.', settings.get("emmet_scope"), view, locations):
                return (cssStyleCompletion.returnSymbolCompletions(view, 'class'), sublime.INHIBIT_WORD_COMPLETIONS)
            if location.at_style_symbol('#', settings.get("emmet_scope"), view, locations):
                return (cssStyleCompletion.returnSymbolCompletions(view, 'id'), sublime.INHIBIT_WORD_COMPLETIONS)

        # inside CSS scope pseudo completions
        if location.at_style_symbol(':', settings.get("css_completion_scope"), view, locations):
            return (cssStyleCompletion.returnPseudoCompletions(), sublime.INHIBIT_WORD_COMPLETIONS)

        # inside CSS scope symbol completions
        if location.at_style_symbol('.', settings.get("css_completion_scope"), view, locations):
            return (cssStyleCompletion.returnSymbolCompletions(view, 'class'), sublime.INHIBIT_WORD_COMPLETIONS)
        if location.at_style_symbol('#', settings.get("css_completion_scope"), view, locations):
            return (cssStyleCompletion.returnSymbolCompletions(view, 'id'), sublime.INHIBIT_WORD_COMPLETIONS)

        # inside LESS scope symbol completions
        if location.at_style_symbol(
            '@', 'source.less',
            view, locations
        ):
            return (
                cssStyleCompletion.returnSymbolCompletions(
                    view, 'less_var'
                ), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        if location.at_style_symbol(
            '.', 'source.less - parameter.less',
            view, locations
        ):
            return (
                (cssStyleCompletion.returnSymbolCompletions(
                    view, 'less_mixin'
                ) + cssStyleCompletion.returnSymbolCompletions(
                    view, 'class'
                )), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        # inside SCSS scope symbol completions
        if location.at_style_symbol(
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
            'meta.property-list.scss meta.at-rule.include.scss - punctuation.section.function.scss'
        ):
            return (
                cssStyleCompletion.returnSymbolCompletions(
                    view , 'scss_mixin'
                ), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        return None

if ST2:
    plugin_loaded()
