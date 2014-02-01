import sublime

ST2 = int(sublime.version()) < 3000
settings = None


def plugin_loaded():
	global settings
	settings = sublime.load_settings('css_style_completions.sublime-settings')


def get(key, default=None):
	global settings

	if settings:
		return settings.get(key, default)
	else:
		return default


if ST2:
	plugin_loaded()
