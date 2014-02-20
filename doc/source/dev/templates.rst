Creating Custom Templates
=========================

Boss templates are extremely easy to write.  A basic template consists of the
following:

    * A boss.yml config file
    * One or more files/directories to copy for new projects

Boss doesn't care what the contents of template files are, as long as it is
a readable file.  The following is an example python template:

.. code-block:: text

    -> python
        `----> @module@/
                `----> @module@.py

        `----> setup.py
        `----> setup.cfg
        `----> README
        `----> LICENSE
        `----> boss.yml


In this example, '@module@' is a variable defined in the 'boss.yml' config
for this template.  When calling 'boss create -t local:python' Boss will ask
the user to supply a value for '@module@', and then when files/directories
are copied that value will be replace at every occurrence of '@module@' both
in file/directory names as well as file contents.


Boss Template Configuration Files
---------------------------------

Currently Boss only supports a 'boss.json' or boss.yml configuration file
which is in the JSON or Yaml format respectively.  The following is an example
Yaml configuration file:

.. code-block:: text

    variables:
        version: Version
        module: Python Module Name
        class_prefix: Python Class Prefix
        project: Project Name
        description: Project Description
        creator: Project Creator
        email: Project Creator Email
        url: Project URL
        license: Project License

    external_files:
        .gitignore: https://raw.github.com/github/gitignore/master/Python.gitignore
        LICENSE: https://raw.github.com/datafolklabs/license/master/@license@


The 'variables' setting is a list of key/value pairs.  The first item in the
list is the variable that is set, and the second is the question as presented
to the user for input.

The 'external_files' is also a list of key/value pairs, and is optional.
These are files that are pulled down externally.  The first item in the
external file definition is the destination path where that file should be
saved to.  The second is the remote URL to pull the contents from.  In the
above example we use external files to pull down a current .gitignore file
from Github, as well as a LICENSE file for the given license if it exists.

Working with Variables
----------------------

Boss treats all variables as strings.  Therefore, it supports string
operations during the replacement process.  For example, if I had a variable
of 'foo', then in my templates I would reference that variable as '@foo@'.  If
the value of '@foo@' were 'bar' for example, I could do things like:

    * @foo.capitalize@ => Bar
    * @foo.upper@ => BAR
    * @foo.lower@ => bar
    * @foo.title@ = Bar

These simple string operations are commonly used throughout templates.  That
said, don't get carried away ... Boss doesn't intend to be a robust templating
language, but rather a facility to easily build and copy templates for new
projects.

Delimiter
---------

The default delimiter is '@'.  In some cases, this might not work for your
template.  You can change this in your boss.yml or boss.json config:

.. code-block:: text

    delimiter: '%'
