import sublime


def get(key, default=None):
	settings = sublime.load_settings('css_style_completions.sublime-settings')
	if settings:
		return settings.get(key, default)
	else:
		return default
