CSS Extended Completions
===================

###Sublime Text 2/3

✓	Extended property/value CSS completions

✓	Class completions

✓	ID completions

✓	pseudo selector completions

✓	LESS variable completions

✓	LESS mixin completions

✓	SCSS variable completions

✓	SCSS mixin completions

Caches completions on document save.

* If the document is a .css file (stand alone file) it will add any symbols that are found to the main project index.

* If the document is a .html/.php it will parse that file and extract any classes/IDs found within style tags and only show you those completions, plus any from the main project cache.

property/value completions such as `box-sizing`, additional font names for `font-family`, `animation`, `flex-box`, etc...

You can delete the cache via the command palette `CSS Completions: Delete Cache`

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

