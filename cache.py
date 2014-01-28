import sublime, os

file_path = ''

if int(sublime.version()) < 3000:
    file_path = os.path.join(
        sublime.packages_path(),
        '..',
        'Cache',
        'CSS',
        'CSS.completions.cache'
    )

else:
    file_path = os.path.join(
        sublime.cache_path(),
        'CSS',
        'CSS.completions.cache'
    )

file_path = os.path.abspath(file_path)
cache_dir = file_path.replace('CSS.completions.cache', '')

if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)


def load():
    import json
    try:
        with open(file_path, 'r') as json_data:
            return json.loads(json_data.read())
    except:
        return {}
