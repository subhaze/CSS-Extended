import sublime, sublime_plugin, re

ST2 = int(sublime.version()) < 3000
if ST2:
    import settings
else:
    from . import settings


def extended_common():
    return {
        "color": ["rgb($1)", "rgba($1)", "hsl($1)", "hsla($1)", "transparent"],
        "uri": ["url($1)"],
        "border-style": ["none", "hidden", "dotted", "dashed", "solid", "double", "groove", "ridge", "inset", "outset"],
        "border-width": ["thin", "medium", "thick"],
        "box": ["border-box", "padding-box", "content-box"],
        "shape": ["rect($1)"],
        "generic-family": ["serif", "sans-serif", "cursive", "fantasy", "monospace"],
        "family-name": settings.get('font_list', [])
    }

extended_css_data = """
"font-family"=<family-name> | <generic-family>| inherit
"display"=flex | inline-flex | compact | container | run-in
"icon"=auto | <uri> | inherit
"box-sizing"=content-box | padding-box | border-box | inherit
"outline-offset"=<length> | inherit
"resize"=none | both | horizontal | vertical | inherit
"text-overflow"=clip | ellipsis | inherit
"cursor"=<uri> | auto | default | none | context-menu | help | pointer | progress | wait | cell | crosshair | text | vertical-text | alias | copy | move | no-drop | not-allowed | e-resize | n-resize | ne-resize | nw-resize | s-resize | se-resize | sw-resize | w-resize | ew-resize | ns-resize | nesw-resize | nwse-resize | col-resize | row-resize | all-scroll | zoom-in | zoom-out | inherit
"nav-index"=auto | <number> | inherit
"nav-up" "nav-right" "nav-down" "nav-left"=auto | current | root | inherit
"ime-mode"=auto | normal | active | inactive | disabled | inherit

"flex-basis"=<percentage> | <number> | inherit | auto
"flex-direction"=row | row-reverse | column | column-reverse | inherit
"flex-flow"=<flex-direction> | <flex-wrap>
"flex-grow"=<number> | inherit
"flex-shrink"=<number> | inherit
"flex-wrap"=nowrap | wrap | wrap-reverse | inherit
"justify-content"=flex-start | flex-end | center | space-between | space-around
"order"=<number> | inherit
"align-content"=flex-start | flex-end | center | space-between | space-around | stretch | inherit
"align-items"=flex-start | flex-end | center | baseline | stretch | inherit
"align-self"=auto | flex-start | flex-end | center | baseline | stretch | inherit

"transform"=none | <transform-list>
"transform-origin"=left | center | right | top | bottom | <percentage> | <length>
"transform-style"=flat | preserve-3d
"perspective"=none | <length>
"perspective-origin"=left | center | right | top | bottom | <percentage> | <length>
"backface-visibility"=visible | hidden

"text-transform"=none | capitalize | uppercase | lowercase | full-width
"white-space"=normal | pre | nowrap | pre-wrap | pre-line
"tab-size"=<integer> | <length>
"line-break"=auto | loose | normal | strict
"word-break"=normal | keep-all | break-all
"hyphens"=none | manual | auto
"overflow-wrap"=normal | break-word
"word-wrap"=normal | break-word
"text-align"=start | end | left | right | center | justify | match-parent | start end
"text-align-last"=auto | start | end | left | right | center | justify
"text-justify"=auto | none | inter-word | distribute
"word-spacing"=normal | <length> | <percentage>
"letter-spacing"=normal | <length>
"text-indent"=<length> | <percentage> | hanging | each-line
"hanging-punctuation"=none | first | force-end | allow-end | last

"backface-visibility"=visible | hidden
"transition-property"=none | <single-transition-property>
"transition-duration"=<number>
"transition-timing-function"=<single-transition-timing-function>
"transition-delay"=<number>
"transition"=<single-transition>

"animation-name"=none
"animation-duration"=<number>
"animation-timing-function"=ease | steps($1, start)$0 | steps($1, end)$0 | step-start | step-end | linear | ease-out | ease-in-out | ease-in | cubic-bezier($1, $2, $3, $4)$0
"animation-iteration-count"=1 | infinite | <number>
"animation-direction"=normal | reverse | alternate-reverse | alternate
"animation-play-state"=running | paused
"animation-delay"=<number>
"animation-fill-mode"=none | forwards | both | backwards
"animation"=<animation-duration> | <animation-timing-function> | <animation-delay> | <animation-iteration-count> | <animation-direction> | <animation-fill-mode> | <animation-play-state>

"font-family"=<family-name> | <generic-family>
"font-weight"=normal | bold | bolder | lighter | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900
"font-stretch"=normal | ultra-condensed | extra-condensed | condensed | semi-condensed | semi-expanded | expanded | extra-expanded | ultra-expanded
"font-style"=normal | italic | oblique
"font-size"=<absolute-size> | <relative-size> | <length> | <percentage>
"font-size-adjust"=none | <number>
"font"=<font-style> | <font-variant-css21> | <font-weight> | <font-stretch> | <font-size> | <line-height> | <font-family> | caption | icon | menu | message-box | small-caption | status-bar
"font-synthesis"=none | weight | style
"font-kerning"=auto | normal | none
"font-variant-ligatures"=normal | none | <common-lig-values> | <discretionary-lig-values> | <historical-lig-values> | <contextual-alt-values>
"font-variant-position"=normal | sub | super
"font-variant-caps"=normal | small-caps | all-small-caps | petite-caps | all-petite-caps | unicase | titling-caps
"font-variant-numeric"=normal | <numeric-figure-values> | <numeric-spacing-values> | <numeric-fraction-values> | ordinal | slashed-zero
"font-variant-alternates"=normal | stylistic(<feature-value-name>) | historical-forms | styleset(<feature-value-name>) | character-variant(<feature-value-name>) | swash(<feature-value-name>) | ornaments(<feature-value-name>) | annotation(<feature-value-name>)
"font-variant-east-asian"=normal | <east-asian-variant-values> | <east-asian-width-values> | ruby
"font-variant"=normal | none | <common-lig-values> | <discretionary-lig-values> | <historical-lig-values> | <contextual-alt-values> | stylistic(<feature-value-name>) | historical-forms | styleset(<feature-value-name>) | character-variant(<feature-value-name>) | swash(<feature-value-name>) | ornaments(<feature-value-name>) | annotation(<feature-value-name>) | small-caps | all-small-caps | petite-caps | all-petite-caps | unicase | titling-caps | <numeric-figure-values> | <numeric-spacing-values> | <numeric-fraction-values> | ordinal | slashed-zero | <east-asian-variant-values> | <east-asian-width-values> | ruby
"font-feature-settings"=normal | <feature-tag-value>
"font-language-override"=normal | <string>
"""


def parse_css_data(data):
    props = {}
    for l in data.splitlines():
        if l == "":
            continue

        names, values = l.split('=')

        allowed_values = []
        for v in values.split('|'):
            v = v.strip()
            if v[0] == '<' and v[-1] == '>':
                key = v[1:-1]
                if key in extended_common():
                    allowed_values += extended_common()[key]
            else:
                allowed_values.append(v)

        for e in names.split():
            if e[0] == '"':
                props[e[1:-1]] = sorted(allowed_values)
            else:
                break

    return props


class CSSCompletions(sublime_plugin.EventListener):
    props = None
    rex = None

    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "source.stylus, source.scss - meta.selector.css, source.less - meta.selector.css, source.css - meta.selector.css"):
            return []

        if not self.props:
            self.props = parse_css_data(extended_css_data)
            self.rex = re.compile("([a-zA-Z-]+):\s*$")

        l = []
        if (
            view.match_selector(locations[0], "meta.property-value.css, meta.property-value.scss")
            # This will catch scenarios like .foo {font-style: |}
            or view.match_selector(locations[0] - 1, "meta.property-value.css, meta.property-value.scss")
        ):
            loc = locations[0] - len(prefix)
            line = view.substr(sublime.Region(view.line(loc).begin(), loc))

            m = re.search(self.rex, line)
            if m:
                prop_name = m.group(1)
                if prop_name in self.props:
                    values = self.props[prop_name]

                    add_semi_colon = view.substr(sublime.Region(locations[0], locations[0] + 1)) != ';'

                    for v in values:
                        desc = v
                        snippet = v

                        if add_semi_colon:
                            snippet += ";"

                        if snippet.find("$1") != -1:
                            desc = desc.replace("$1", "")

                        l.append((desc, snippet))

                    return (l, sublime.INHIBIT_WORD_COMPLETIONS)

            return None
        else:
            add_colon = not view.match_selector(locations[0], "meta.property-name.css")

            for p in self.props:
                if add_colon:
                    l.append((p, p + ": "))
                else:
                    l.append((p, p))

            return (l, sublime.INHIBIT_WORD_COMPLETIONS)
