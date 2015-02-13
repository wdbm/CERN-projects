#!/usr/bin/env python

"""
################################################################################
#                                                                              #
# compile_documentation                                                        #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program compiles Markdown documentation to HTML documentation suitable  #
# for CERN Subversion repositories and CERN Git repositories. It does this     #
# using Pandoc and online CSS.                                                 #
#                                                                              #
# copyright (C) 2015 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

Usage:
    program [options]

Options:
    -h, --help                 display help message
    --version                  display version and exit
    --MarkdownFileName=FILE    Markdown file [default: README.md]
    --HTMLSVNFileName=FILE     SVN HTML file [default: README_SVN.html]
    --HTMLGitFileName=FILE     Git HTML file [default: README.html]
"""

name    = "compile_documentation"
version = "2015-02-13T2009Z"

import os
import sys
import subprocess
import docopt
import distutils.version

def main(options):

    MarkdownFileName = options["--MarkdownFileName"]
    HTMLSVNFileName  = options["--HTMLSVNFileName"]
    HTMLGitFileName  = options["--HTMLGitFileName"]

    ensure_program_available("pandoc")
    ensure_version_Pandoc()
    compile_documentation_SVN(
        MarkdownFileName = MarkdownFileName,
        HTMLSVNFileName  = HTMLSVNFileName
    )
    compile_documentation_Git(
        HTMLSVNFileName  = HTMLSVNFileName,
        HTMLGitFileName  = HTMLGitFileName
    )

def ensure_file_existence(fileName):
    if not os.path.isfile(os.path.expandvars(fileName)):
        print("file {fileName} does not exist".format(
            fileName = fileName
        ))
        sys.exit()

def which(program):
    def is_exe(fpath):
        return(os.path.isfile(fpath) and os.access(fpath, os.X_OK))
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return(program)
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return(exe_file)
    return(None)

def ensure_program_available(program):
    if which(program) is None:
        print("program {program} not available".format(
            program = program
        ))
        sys.exit()

def get_version_Pandoc():
    process = subprocess.Popen(["pandoc", "--version"], stdout=subprocess.PIPE)
    output, error = process.communicate()
    version = output.split("\n")[0].split(" ")[1]
    return(version)

def ensure_version_Pandoc():
    versionMinimumRequired = "1.12.2.1"
    versionCurrent  = get_version_Pandoc()
    if distutils.version.LooseVersion(versionCurrent) < \
    distutils.version.LooseVersion(versionMinimumRequired):
        print("Pandoc version >= {version} required".format(
            version = versionMinimumRequired
        ))
        sys.exit()

def compile_documentation_SVN(
    MarkdownFileName = None,
    HTMLSVNFileName  = None
    ):
    ensure_file_existence(MarkdownFileName)
    process = subprocess.Popen([
        "pandoc",
        "-c",
        "https://cdn.rawgit.com/wdbm/style/master/SS/newswire.css",
        MarkdownFileName
    ], stdout = subprocess.PIPE)
    output, error = process.communicate()
    HTMLSVNFileContent = output
    with open(HTMLSVNFileName, "w") as HTMLSVNFile:
        HTMLSVNFile.write(HTMLSVNFileContent)

def compile_documentation_Git(
    HTMLSVNFileName = None,
    HTMLGitFileName = None
    ):
    ensure_file_existence(HTMLSVNFileName)
    lineRemovalPatterns = [
        "!DOCTYPE html",
        "<html",
        "<head",
        "<meta",
        "<title",
        "<link rel",
        "</head>",
        "<body>",
        "</body>",
        "</html>"
    ]
    # Create a variable for resultant Git file content.
    HTMLGitFileContent = ""
    # Loop over the lines of the HTML SVN file, building the resultant Git file
    # content. If any of the line removal patterns are in a line, remove that
    # line.
    HTMLSVNFile = open(HTMLSVNFileName, "r")
    for line in HTMLSVNFile:
        if not any(pattern in line for pattern in lineRemovalPatterns):
            HTMLGitFileContent = HTMLGitFileContent + line
    # Add CSS.
    CSS_addition = """
</style>
<style>
pre{
    border-radius: 0.5em;
    border-left: 1px solid #000000;
    border-right: 1px solid #000000;
    border-top: 1px solid #000000;
    border-bottom: 1px solid #000000;
    background: #F9F9F9;
    color: #000000;
    padding: 1.5em;
}

/* list point formatting */

.img-rounded{
    -webkit-border-radius: 6px;
    -moz-border-radius: 6px;
    border-radius: 6px;
}

.img-polaroid{
    padding: 4px;
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border:1px solid rgba(0, 0, 0, 0.2);
    -webkit-box-shadow:0 1px 3px rgba(0, 0, 0, 0.1);
    -moz-box-shadow:0 1px 3px rgba(0, 0, 0, 0.1);
    box-shadow:0 1px 3px rgba(0, 0, 0, 0.1);
}

.img-circle{
    -webkit-border-radius: 500px;
    -moz-border-radius: 500px;
    border-radius: 500px;
}

/* tables */

/* left margin on pages */
.container,
.navbar-static-top .container,
.navbar-fixed-top .container,
.navbar-fixed-bottom
.container{
    width: 940px;
}
.container{
    margin-right: auto;
    margin-left:auto;
    *zoom: 1;
}
.container:before,.container:after{
    display: table;
    content: "";
    line-height: 0;
}

/* remove unnecessary border spacings */
table{
    max-width: 100%;
    background-color: transparent;
    border-collapse: collapse;
    border-spacing:0;
}

/* extend tables across the full page width, rather than limiting them to the
 * minimum size */
.table{
    width: 100%;
    margin-bottom: 21px;
}
.table th,
.table td{
    padding: 8px;
    line-height: 21px;
    text-align: left;
    vertical-align: top;
    border-top: 1px solid #dddddd;
}

/* thin table top border */
.table caption+thead tr: first-child th,
.table caption+thead tr:first-child td,
.table colgroup+thead tr:first-child th,
.table colgroup+thead tr:first-child td,
.table thead:first-child tr:first-child th,
.table thead:first-child tr:first-child td{
    border-top: 0;
}

.table-bordered th,
.table-bordered td{
    border-left:1px solid #000000;
}

/* table alternating line colours */
.table-striped tbody tr:nth-child(odd) td,
.table-striped tbody tr:nth-child(odd) th{
    background-color: #f9f9f9;
}

table{
    width: 100%;
    margin-bottom: 21px;
    max-width: 100%;
    background-color: transparent;
    border-collapse: collapse;
    border-spacing:0;
    /* table bordered */
    border:1px solid #000000;
    border-collapse:separate;
    *border-collapse:collapse;
    border-left:0;
    -webkit-border-radius:4px;
    -moz-border-radius:4px;
    border-radius:4px;
}

th,
td{
    padding: 8px;
    line-height: 21px;
    text-align: left;
    vertical-align: top;
    border-top: 1px solid #dddddd;
    border-left: 1px solid #000000;
}

/* table alternating line colours */
tbody tr:nth-child(odd) td,
tbody tr:nth-child(odd) th{
    background-color: #f9f9f9;
}
</style>
    """
    HTMLGitFileContent = HTMLGitFileContent.replace("</style>", CSS_addition, 1)
    with open(HTMLGitFileName, "w") as HTMLGitFile:
        HTMLGitFile.write(HTMLGitFileContent)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
