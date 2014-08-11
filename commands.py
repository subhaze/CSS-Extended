import sublime, sublime_plugin, re

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
    symbol_snippet = view.substr(sublime.Region(region.b, end_region.a)).strip()
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
    end_region = view.find(r'(?<!\@)\{|(\)\s*\}|(\)\s*;))', region.b)
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
    'less_var': 'variable.declaration.less',
    'less_mixin': 'entity.other.less.mixin',
    'scss_var': 'variable.scss',
    'scss_mixin': 'meta.at-rule.mixin.scss entity.name.function.scss',
    'scss_placeholder': 'entity.other.attribute-name.placeholder.scss',

    # Define commands for each symbol type...
    'class_command': simpleCompletionSet,
    'id_command': simpleCompletionSet,
    'less_var_command': simpleCompletionSet,
    'less_mixin_command': lessMixinCompletionSet,
    'scss_var_command': simpleCompletionSet,
    'scss_mixin_command': scssMixinCompletionSet,
    'scss_placeholder_command': simpleCompletionSet
}


class CssExtendedCompletionSetSettingCommand(sublime_plugin.ApplicationCommand):

    """Enables/Disables settings"""

    def run(self, setting):
        s = sublime.load_settings('css_style_completions.sublime-settings')
        s.set(setting, not s.get(setting, False))
        sublime.save_settings('css_style_completions.sublime-settings')

    def is_checked(self, setting):
        s = sublime.load_settings('css_style_completions.sublime-settings')
        return s.get(setting, False)
