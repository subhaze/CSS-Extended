CSS Extended Completions
===================

###Sublime Text 2/3

Lazy loads in CSS completions.

A, somewhat, intelligent CSS class completion package for Sublime Text 2 and Sublime Text 3.


It will lazy parse CSS class when you save a document that you're working on. If that document is a .css file (stand alone file) it will add any classes that are found to the main project index.

When you save a .html/.php it will parse that file and extract any classes found within style tags and only show you those completions, plus any from the main project cache. In other words, it will cache non-standalone documents on a per file basis and any stand alone document (.css files) to the main project cache.

You can delete the cache via the command palette `CSS Completions: Delete Cache`
