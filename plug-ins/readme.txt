Directory contains plugins that test GimpFu features

Each in its own directory to mirror how they must be installed.
Each plugin main .py file must have execute permission.

The test plugins don't all pass.
When I find a plugin that fails on some little used corner case,
or where the plugin is obviously second rate or hard to understand, I move on.
When I find another failure I have seen before, I might then address the issue.
My intent was to explore depth first.
I.E. find many issues, fix the important ones,
especially issues that seem pop up again and seem to prevent finding more issues.
