CSS Extended Completions
===================

###Sublime Text 2/3

----

####Completion Cache

Caches completions on document save.

* If the document is a .css file (stand alone file) it will add any symbols that are found to the main project index.

* If the document is a .html/.php/etc... it will parse that file and extract any classes/IDs found within style tags and only show you those completions within that file, plus any from the main project cache.

----

####Loading External Files

You can eager load files from folders outside of your project via `load_external_files` setting.

Example: `"load_external_files": ["/abs/path/to/css/*.css", "/abs/path/to/less/*.less"]`

----

####Property/Value Completions

property/value completions such as `box-sizing`, additional font names for `font-family`, `animation`, `flex-box`, etc...

You can delete the cache via the command palette `CSS Completions: Delete Cache`

----

#### [Emmet](http://emmet.io) Support

Emmet support is enabled by default, you just need to add the following to your User Settings:

```json
"auto_complete_selector": "source - comment, meta.tag - punctuation.definition.tag.begin, text.html.basic"
```

Don't have Emmet? No problem, you won't have any problems with it being enable by default.  
Still want to disable Emmet support? Just set `"use_emmet": false` in the user's package settings

### CSS Completion Examples
----
####Pseudo Selector Completions

![](https://dl.dropboxusercontent.com/u/4790638/images/ST-pseudo-selector.png)

----
#### Extended Property Value Completions

![](https://dl.dropboxusercontent.com/u/4790638/images/ST-extended-css-property-values-2.png)

----
#### Class Completions Within Class Attribute
![](https://dl.dropboxusercontent.com/u/4790638/images/ST-class-completion-in-class-attribute-2.png)

----
#### Class Completions Within CSS Scope
![](https://dl.dropboxusercontent.com/u/4790638/images/ST-class-completion-in-css.png)

### LESS Completion Examples
----
####Mixin Completions, with Parametric Mixin Tab Order
![](https://dl.dropboxusercontent.com/u/4790638/images/ST-LESS-mixin-completions.png)
![](https://dl.dropboxusercontent.com/u/4790638/images/ST-LESS-mixin-completions-with-snippet-tabbing.png)

### SCSS Completion Examples
----
####Mixin Completions, with Parametric Mixin Tab Order
![](https://dl.dropboxusercontent.com/u/4790638/images/ST-SCSS-mixin-completions.png)
![](https://dl.dropboxusercontent.com/u/4790638/images/ST-SCSS-mixin-completions-with-snippet-tabbing.png)

