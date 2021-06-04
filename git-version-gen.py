#!/usr/bin/env python3

"""
git-version-gen.py -- Generate git-version.h if repository has changed.

Copyright (C) 2021  Lloyd Konneker

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


Usage: git-version-gen.py

Must be run in the build tree.
git must be installed.

Side effect on the build tree:
if git-version.h not exist, create
else if existing git-version.h is stale compared to repository, overwrite git-version.h

Derived from the automake build process for GIMP.
Named after the automake shell script git-version-gen.sh.
"""

import subprocess

def get_git_long_revision():
    return subprocess.check_output(["git", "describe", "--always"]).strip()

def get_git_short_revision():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()

def get_git_last_commit_year():
    return subprocess.check_output(['git', 'log', '-n1', '--date=format:%Y', '--pretty=%cd',]).strip()

# fallback: 'unknown (unsupported)',


# Generate a new contents of git-version.h, from a template
with open('workfile') as f:
    template = f.read()

template.replace('@GIMP_GIT_VERSION@', get_git_long_revision())
template.replace('@GIMP_GIT_VERSION_ABBREV@', get_git_short_revision())
template.replace('@GIMP_GIT_LAST_COMMIT_YEAR@', get_git_last_commit_year())

# if exists
# compare
# if stale, overwrite
