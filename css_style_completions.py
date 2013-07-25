import sublime, sublime_plugin

class CssStyleCompletions(sublime_plugin.EventListener):
	def on_query_completions(self, view, prefix, locations):
		selector = view.match_selector(locations[0], 'text.html string')
		attribute = view.expand_by_class(locations[0], sublime.CLASS_PUNCTUATION_START | sublime.CLASS_PUNCTUATION_END, '"\'')
		start = attribute.begin() - 7
		end = attribute.end()
		attribute = view.substr(sublime.Region(start, end))
		if selector and attribute.startswith('class'):
			results = []
			for _view in sublime.active_window().views():
				results += [(_view.substr(point).replace('.','').replace('#','') + "\t CSS", _view.substr(point).replace('.','').replace('#','')) for point in _view.find_by_selector('entity.other.attribute-name')]
			results = list(set(results))
			return (results, 0)
		if selector and attribute.startswith(('style')):
			print(prefix, 'prefix')
			return [
				('body\tCSS property', 'body:')
			]