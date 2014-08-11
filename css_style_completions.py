import sublime, sublime_plugin, os
ST2 = int(sublime.version()) < 3000

if ST2:
    # ST 2
    import completions
    import cache
    import settings
    import location
    import style_parser
else:
    # ST 3
    from . import completions
    from . import cache
    from . import settings
    from . import location
    from . import style_parser


def plugin_loaded():
    cache.load()
    style_parser.init_file_loading()


class CssStyleCompletionPruneCacheCommand(sublime_plugin.WindowCommand):
    """Removes missing files from the cache"""

    def run(self):
        cache.prune_cache()


class CssStyleCompletionDeleteCacheCommand(sublime_plugin.WindowCommand):
    """Deletes all cache that plugin has created"""

    def run(self):
        cache.remove_cache()
        cache.projects_cache = {}


class AddToCacheCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], name="", file_type="*.*"):
        import glob
        current_delay = 500
        for path in paths:
            if os.path.isdir(path):
                sublime.set_timeout(lambda: style_parser.load_files(
                    glob.glob(path + os.path.sep + file_type),
                    as_scratch=False
                ), current_delay)
                current_delay = current_delay + 100


class CssStyleCompletionEvent(sublime_plugin.EventListener):
    #TODO: DRY up the sync/async logic
    def on_post_save(self, view):
        if not ST2:
            return
        file_name = view.file_name()
        if not file_name:
            return
        style_parser.load_linked_files(view)
        style_parser.parse_view(view)

    def on_post_save_async(self, view):
        file_name = view.file_name()
        if not file_name:
            return
        style_parser.load_linked_files(view)
        style_parser.parse_view(view)

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
                completions.returnSymbolCompletions(view, 'class'),
                sublime.INHIBIT_WORD_COMPLETIONS
            )

        id_attr = location.at_html_attribute('id', view, locations)
        if id_attr and html_attr_scope:
            return (
                completions.returnSymbolCompletions(view, 'id'),
                sublime.INHIBIT_WORD_COMPLETIONS
            )

        # inside HTML with Emmet completions
        if settings.get("use_emmet"):
            if location.at_style_symbol('.', settings.get("emmet_scope"), view, locations):
                return (completions.returnSymbolCompletions(view, 'class'), sublime.INHIBIT_WORD_COMPLETIONS)
            if location.at_style_symbol('#', settings.get("emmet_scope"), view, locations):
                return (completions.returnSymbolCompletions(view, 'id'), sublime.INHIBIT_WORD_COMPLETIONS)

        # inside CSS scope pseudo completions
        if location.at_style_symbol(':', settings.get("css_completion_scope"), view, locations):
            return (completions.returnPseudoCompletions(), sublime.INHIBIT_WORD_COMPLETIONS)

        # inside CSS scope symbol completions
        if location.at_style_symbol('.', settings.get("css_completion_scope"), view, locations):
            return (completions.returnSymbolCompletions(view, 'class'), sublime.INHIBIT_WORD_COMPLETIONS)
        if location.at_style_symbol('#', settings.get("css_completion_scope"), view, locations):
            return (completions.returnSymbolCompletions(view, 'id'), sublime.INHIBIT_WORD_COMPLETIONS)

        # inside LESS scope symbol completions
        if location.at_style_symbol(
            '@', 'source.less',
            view, locations
        ):
            return (
                completions.returnSymbolCompletions(
                    view, 'less_var'
                ), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        if location.at_style_symbol(
            '.', 'source.less - parameter.less',
            view, locations
        ):
            return (
                (completions.returnSymbolCompletions(
                    view, 'less_mixin'
                ) + completions.returnSymbolCompletions(
                    view, 'class'
                )), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        # inside SCSS scope symbol completions
        if location.at_style_symbol(
            '.', 'source.scss',
            view, locations
        ):
            return (
                completions.returnSymbolCompletions(
                    view, 'class'
                ), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        if location.at_style_symbol(
            '%', 'source.scss',
            view, locations
        ):
            return (
                completions.returnSymbolCompletions(
                    view, 'scss_placeholder'
                ), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        if location.at_style_symbol(
            '$', 'source.scss, meta.property-value.scss',
            view, locations
        ):
            return (
                completions.returnSymbolCompletions(
                    view, 'scss_var'
                ), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        if view.match_selector(
            locations[0],
            'meta.property-list.scss meta.at-rule.include.scss - punctuation.section.function.scss'
        ):
            return (
                completions.returnSymbolCompletions(
                    view , 'scss_mixin'
                ), sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
            )

        # return element list
        if view.match_selector(
            locations[0],
            'source.stylus, source.css - meta.property-value.css, source.less - meta.property-value.css, source.scss - meta.property-value.scss'
        ):
            return (completions.returnElementCompletions(), sublime.INHIBIT_WORD_COMPLETIONS)

        return None

if ST2:
    plugin_loaded()
