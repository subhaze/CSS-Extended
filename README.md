CSS Extended Completions
===================

###Sublime Text 2/3

---

####Issue Reporting

**Please include the following information when submitting a ticket**
- Sublime Text version
- OS
- any related error that you can find in the Sublime Text console (ctrl+`) if no related error is found please state that you saw no errors in the console.

This plug-in is beta quality so please file any issues you run into here: https://github.com/subhaze/CSS-Extended/issues?state=open

---
###Features
- CSS class completions within HTML class attributes (class="|") and CSS files
- ID completions within HTML id attributes (id="|") and CSS files
- LESS variable and mixin completions (with parametric tab-stops)
- SCSS variable and mixin completions (with parametric tab-stops)
- element completions within CSS files
- pseudo selector completions within CSS files
- font stack completions within the `font-family:` property
- a more up-to-date property/value completion list within CSS files
- parse linked style sheets in HTML files, can be disabled via `index_linked_style_sheets` setting

---
###Usage

#### Load Files From Side Bar Menu

You can add files from the side bar, just right click on a folder and select the type of files you'd like to load via `CSS Extended Completions > [file type(s)]`

This is *not* a recursive process, so, only the immediate files in the folder are processed, the subfolders are not processed.

![](https://dl.dropboxusercontent.com/u/4790638/images/ST-load-files-from-side-bar.png)

----

####Cache On Save

Caches completions on document save.

* If the document is a .css file (stand alone file) it will add any symbols that are found to the main project index.

* If the document is a .html/.php/etc... it will parse that file and extract any classes/IDs found within style tags and only show you those completions within that file, plus any from the main project cache.

----

####Loading External Files

You can eager load files from folders outside of your project via `load_external_files` setting.

Example: `"load_external_files": ["/abs/path/to/css/*.css", "/abs/path/to/less/*.less"]`

----

####Deleting Cache File

You can delete the cache via the command palette `CSS Completions: Delete Cache`

----

####Pruning Cache File

You can remove missing/moved files from the cache via the command palette `CSS Completions: Prune Cache`

----

####Property/Value Completions

property/value completions such as `box-sizing`, additional font names for `font-family`, `animation`, `flex-box`, etc...

----

#### [Emmet](http://emmet.io) Support

Emmet support is enabled by default, you just need to add the following to your User Settings:

```json
"auto_complete_selector": "source - comment, meta.tag - punctuation.definition.tag.begin, text.html.basic"
```

Don't have Emmet? No problem, you won't have any problems with it being enable by default.  
Still want to disable Emmet support? Just set `"use_emmet": false` in the user's package settings or use the `Use Emmet` toggle from the menu `Preferences > Package Settings > CSS Extended Completions`

----

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

