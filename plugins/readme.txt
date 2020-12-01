Plugin source files

All .py

Each in its own directory to mirror how Gimp requires they be installed.
Each plugin main .py file must have execute permission.

The plugins don't all work.

Categories:
- wild: gleaned from the web. Authors are third parties, rarely Gimp.org
- test: unit tests of GimpFu features.  Author self
- nonGimpFu: unit tests of GI's Python plugins.  Author self
- bad: abandoned active testing, horrible.

When I find a plugin that fails on some little used corner case,
or where the plugin is obviously second rate or hard to understand, I move on.
When I find another failure I have seen before, I might then address the issue.
My intent was to explore depth first.
I.E. find many issues, fix the important ones,
especially issues that seem pop up again and seem to prevent finding more issues.
