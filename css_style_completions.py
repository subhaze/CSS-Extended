import sublime, sublime_plugin

class CssStyleCompletions(sublime_plugin.EventListener):
	def on_query_completions(self, view, prefix, locations):
		selector = view.match_selector(locations[0], 'text.html string')
		attribute = view.substr(view.expand_by_class(locations[0], sublime.CLASS_WORD_START | sublime.CLASS_WORD_END, ' >'))
		if selector and attribute.startswith(('class', 'ng-class')):
			results = []
			for _view in sublime.active_window().views():
				results += [(_view.substr(point).replace('.','').replace('#','') + "\t CSS", _view.substr(point).replace('.','').replace('#','')) for point in _view.find_by_selector('entity.other.attribute-name')]
			results = list(set(results))
			return results
		if selector and attribute.startswith(('style')):
			print(prefix, 'prefix')
			return [
				('body\tCSS property', 'body:')
			]