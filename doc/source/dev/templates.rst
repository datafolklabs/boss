Creating Custom Templates
=========================

Boss templates are extremely easy to write.  A basic template consists of the 
following:

    * A boss.json config file
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
        `----> boss.json
        

In this example, '@module@' is a variable defined in the 'boss.json' config
for this template.  When calling 'boss create -t local:python' Boss will ask
the user to supply a value for '@module@', and then when files/directories
are copied that value will be replace at every occurrence of '@module@' both
in file/directory names as well as file contents.


Boss Template Configuration Files
---------------------------------

Currently Boss only support a 'boss.json' configuration file which is 
obviously in the JSON format.  The following is an example configuration file:

.. code-block:: text

    {
        "variables": [
            ["Version", "version"],
            ["Python Module Name", "module"],
            ["Python Class Prefix", "class_prefix"],
            ["Project Name", "project"],
            ["Project Description", "description"],
            ["Project Creator", "creator"],
            ["Project Creator Email", "email"],
            ["License", "license"],
            ["Project URL", "url"]
        ],
        "external_files": [
            [".gitignore", "https://raw.github.com/github/gitignore/master/Python.gitignore"],
            ["LICENSE", "https://raw.github.com/derks/oss-license/master/license"]
        ]
    }
    

The 'variables' setting is a list of lists.  The first item in a list is the
question that is asked to the user, and then second is the variable that value
is stored as.

The 'external_files' is also a list of lists, and is optional.  These are 
files that are pulled down externally.  The first item in an external file 
definition is the destination path where that file should be saved to.  The 
second is the remote URL to pull the contents from.

Working with Variables
----------------------

Boss treats all variables as strings.  Therefore, it supports strings 
operations during the replacement process.  For example, if I had a variable
of 'foo', then in my templates I would reference that variable as '@foo@'.  If 
the value of '@foo@' were 'bar' for example, I could do things like:

    * @foo.capitalize@ => Bar
    * @foo.upper@ => BAR
    * @foo.lower@ => BAR
    
These simple string operations are commonly used throughout templates.  That
said, don't get carried away ... Boss doesn't intent to be a robust templating
language, but rather a facility to copy templates for new projects.

