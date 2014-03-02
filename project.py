import sublime, glob

ST2 = int(sublime.version()) < 3000

if ST2:
    import settings
else:
    from . import settings


def get_external_files():
    external_files = []
    for file_path in settings.get('load_external_files', []):
        external_files.extend(glob.glob(file_path))
    return external_files
