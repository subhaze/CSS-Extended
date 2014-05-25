import re


def at_html_attribute(attribute, view, locations):
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
    check_attribute = check_attribute[::-1].replace('(', '')
    if check_attribute.startswith(attribute):
            return True
    return False


def at_style_symbol(style_symbol, style_scope, view, locations):
    selector = view.match_selector(locations[0]-1, style_scope)
    if not selector:
        return False
    check_attribute = ''
    view_point = locations[0] - 1
    char = ''
    while(
        char != style_symbol and not re.match(r'[\n ]', char)
        and view_point > -1
    ):
        char = view.substr(view_point)
        check_attribute += char
        view_point -= 1
    check_attribute = check_attribute[::-1]
    if check_attribute.startswith(style_symbol):
        return True
    return False
