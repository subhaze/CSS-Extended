import sublime, sublime_plugin
import re


common = {  "color": ["rgb($1)", "rgba($1)", "hsl($1)", "hsla($1)", "transparent"],
            "uri": ["url($1)"],
            "border-style": ["none", "hidden", "dotted", "dashed", "solid", "double", "groove", "ridge", "inset", "outset"],
            "border-width": ["thin", "medium", "thick"],
            "box": ["border-box", "padding-box", "content-box"],
            "shape": ["rect($1)"],
            "generic-family": ["serif", "sans-serif", "cursive", "fantasy", "monospace"],
            "family-name": ['Georgia', '"Palatino Linotype"', '"Book Antiqua"', 'Palatino', '"Times New Roman"', 'Times', 'Arial', 'Helvetica', '"Arial Black"', 'Gadget', 'Impact', 'Charcoal', '"Lucida Sans Unicode"', '"Lucida Grande"', 'Tahoma', 'Geneva', '"Trebuchet MS"', 'Verdana', 'Geneva', '"Courier New"', 'Courier', '"Lucida Console"', 'Monaco'] }

css_data = """
"background-attachment"=scroll | fixed | inherit
"background-color"=<color> | inherit
"background-image"=<uri> | none | inherit
"background-position"=left | center | right | top | bottom | inherit
"background-repeat"=repeat | repeat-x | repeat-y | no-repeat | inherit
"background"=<color> | <uri> | repeat | repeat-x | repeat-y | no-repeat | scroll | fixed | left | center | right | top | bottom | inherit
"border-collapse"=collapse | separate | inherit
"border-color"=<color> | inherit
"border-spacing"=inherit
"border-style"=<border-style> | inherit
"border-top" "border-right" "border-bottom" "border-left"=<border-width> | <border-style> | <color> | inherit
"border-top-color" "border-right-color" "border-bottom-color" "border-left-color"=<color> | inherit
"border-top-style" "border-right-style" "border-bottom-style" "border-left-style"=<border-style> | inherit
"border-top-width" "border-right-width" "border-bottom-width" "border-left-width"=<border-width> | inherit
"border-width"=<border-width> | inherit
"border"= <border-width> | <border-style> | <color> | inherit
"bottom"=<length> | <percentage> | auto | inherit
"caption-side"=top | bottom | inherit
"clear"=none | left | right | both | inherit
"clip"=<shape> | auto | inherit
"color"=<color> | inherit
"content"=normal | none | <uri> | open-quote | close-quote | no-open-quote | no-close-quote | inherit
"counter-increment"=none | inherit
"counter-reset"=none | inherit
"cursor"=<uri> | auto | crosshair | default | pointer | move | e-resize | ne-resize | nw-resize | n-resize | se-resize | sw-resize | s-resize | w-resize | text | wait | help | progress | inherit
"direction"=ltr | rtl | inherit
"display"=inline | block | list-item | inline-block | table | inline-table | table-row-group | table-header-group | table-footer-group | table-row | table-column-group | table-column | table-cell | table-caption | none | inherit
"empty-cells"=show | hide | inherit
"float"=left | right | none | inherit
"font-family"=<generic-family>| inherit
"font-size"=inherit
"font-style"=normal | italic | oblique | inherit
"font-variant"=normal | small-caps | inherit
"font-weight"=normal | bold | bolder | lighter | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | inherit
"font"=normal | italic | oblique | normal | small-caps | normal | bold | bolder | lighter | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | normal | <generic-family> | caption | icon | menu | message-box | small-caption | status-bar | inherit
"height"=<length> | <percentage> | auto | inherit
"left"=<length> | <percentage> | auto | inherit
"letter-spacing"=normal | <length> | inherit
"line-height"=normal | <number> | <length> | <percentage> | inherit
"list-style-image"=<uri> | none | inherit
"list-style-position"=inside | outside | inherit
"list-style-type"=disc | circle | square | decimal | decimal-leading-zero | lower-roman | upper-roman | lower-greek | lower-latin | upper-latin | armenian | georgian | lower-alpha | upper-alpha | none | inherit
"list-style"=disc | circle | square | decimal | decimal-leading-zero | lower-roman | upper-roman | lower-greek | lower-latin | upper-latin | armenian | georgian | lower-alpha | upper-alpha | none | inside | outside | <uri> | inherit
"margin-right" "margin-left"=<margin-width> | inherit
"margin-top" "margin-bottom"=<margin-width> | inherit
"margin"=<margin-width> | inherit
"max-height"=<length> | <percentage> | none | inherit
"max-width"=<length> | <percentage> | none | inherit
"min-height"=<length> | <percentage> | inherit
"min-width"=<length> | <percentage> | inherit
"opacity"=<number> | inherit
"orphans"=<integer> | inherit
"outline-color"=<color> | invert | inherit
"outline-style"=<border-style> | inherit
"outline-width"=<border-width> | inherit
"outline"=<color> | <border-style> | <border-width> | inherit
"overflow"=visible | hidden | scroll | auto | inherit
"padding-top" "padding-right" "padding-bottom" "padding-left"=<padding-width> | inherit
"padding"=<padding-width> | inherit
"page-break-after"=auto | always | avoid | left | right | inherit
"page-break-before"=auto | always | avoid | left | right | inherit
"page-break-inside"=avoid | auto | inherit
"position"=static | relative | absolute | fixed | inherit
"quotes"=none | inherit
"right"=<length> | <percentage> | auto | inherit
"table-layout"=auto | fixed | inherit
"text-align"=left | right | center | justify | inherit
"text-decoration"=none | underline | overline | line-through | blink | inherit | none
"text-indent"=<length> | <percentage> | inherit
"text-transform"=capitalize | uppercase | lowercase | none | inherit
"top"=<length> | <percentage> | auto | inherit
"unicode-bidi"=normal | embed | bidi-override | inherit
"vertical-align"=baseline | sub | super | top | text-top | middle | bottom | text-bottom | <percentage> | <length> | inherit
"visibility"=visible | hidden | collapse | inherit
"white-space"=normal | pre | nowrap | pre-wrap | pre-line | inherit
"width"=<length> | <percentage> | auto | inherit
"word-spacing"=normal | <length> | inherit
"z-index"=auto | <integer> | inherit


"background-clip"=<box>
"background-origin"=<box>
"background-size"=auto | cover | contain | <percentage> | <length>
"border"=<border-width> | <border-style> | <color>
"border-color"=<color>
"border-image"=<border-image-source> | <border-image-slice> | <border-image-width> | <border-image-width> | <border-image-outset> | <border-image-repeat>
"border-image-outset"=<length> | <number>
"border-image-repeat"=stretch | repeat | round | space
"border-image-slice"=<number> | <percentage>
"border-image-source"=none | <image>
"border-image-width"=<length> | <percentage> | <number> | auto
"border-radius"=<length> | <percentage>
"border-style"=<border-style>
"border-top" "border-right" "border-bottom" "border-left"=<border-width> | <border-style> | <color>
"border-top-color" "border-right-color" "border-bottom-color" "border-left-color"=<color>
"border-top-left-radius" "border-top-right-radius" "border-bottom-right-radius" "border-bottom-left-radius"=<length> | <percentage>
"border-top-style" "border-right-style" "border-bottom-style" "border-left-style"=<border-style>
"border-top-width" "border-right-width" "border-bottom-width" "border-left-width"=<border-width>
"border-width"=<border-width>
"box-decoration-break"=slice | clone
"box-shadow"=none | <shadow> | none
"box-sizing"=<box>



"icon"=auto | <uri> | inherit
"box-sizing"=content-box | padding-box | border-box | inherit
"outline"=<outline-color> | <outline-style> | <outline-width> | inherit
"outline-width"=<border-width> | inherit
"outline-style"=auto | <border-style> | inherit
"outline-color"=<color> | invert | inherit
"outline-offset"=<length> | inherit
"resize"=none | both | horizontal | vertical | inherit
"text-overflow"=clip | ellipsis | inherit
"cursor"=<uri> | auto | default | none | context-menu | help | pointer | progress | wait | cell | crosshair | text | vertical-text | alias | copy | move | no-drop | not-allowed | e-resize | n-resize | ne-resize | nw-resize | s-resize | se-resize | sw-resize | w-resize | ew-resize | ns-resize | nesw-resize | nwse-resize | col-resize | row-resize | all-scroll | zoom-in | zoom-out | inherit
"nav-index"=auto | <number> | inherit
"nav-up" "nav-right" "nav-down" "nav-left"=auto | current | root | inherit
"ime-mode"=auto | normal | active | inactive | disabled | inherit



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
                if key in common:
                    allowed_values += common[key]
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
        if not view.match_selector(locations[0], "source.css - meta.selector.css"):
            return []

        if not self.props:
            self.props = parse_css_data(css_data)
            self.rex = re.compile("([a-zA-Z-]+):\s*$")

        l = []
        if (view.match_selector(locations[0], "meta.property-value.css") or
            # This will catch scenarios like .foo {font-style: |}
            view.match_selector(locations[0] - 1, "meta.property-value.css")):
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
