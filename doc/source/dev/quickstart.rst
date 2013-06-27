Quick Start
===========

The following outlines installation of Boss, as well as quick starting a
few applications from the official repository.

Development Environment
-----------------------

It is recommended to work out of a `VirtualENV <http://pypi.python.org/pypi/virtualenv>`_ 
for development of your application.  That said, you likely don't want to 
install boss every time you start a new project, therefore in this case you 
should consider installing boss to your global system outside of your 
virtualenv.  In most cases you will be creating your project with Boss before
creating a virtualenv anyhow.


Installation
------------

Stable versions of Boss are available via PyPi:

.. code-block:: text

    $ pip install boss
    
To install development versions of Boss you will need to checkout the 'master' 
branch from GitHub.  

.. code-block:: text

    $ pip install -e git+git://github.com/datafolklabs/boss.git#egg=boss
    

Working with Sources
--------------------

Boss supports multiple local and remote (git) template repositories.  You can
see these repositories via the following command:

.. code-block:: text

    $ boss sources

    --        Label: boss
        Source Path: git@github.com:datafolklabs/boss-templates.git
              Cache: /Users/derks/.boss/cache/tmpJDGhlX
         Local Only: False
     Last Sync Time: never


You will notice in the above example that the 'boss' repository has never been
synced (which will be the case on a new install).  To sync templates with 
remote sources, execute the following:

.. code-block:: text

    $ boss sync
    Syncing Boss Templates . . . 
    remote: Counting objects: 137, done.
    remote: Compressing objects: 100% (73/73), done.
    remote: Total 102 (delta 45), reused 83 (delta 26)
    Receiving objects: 100% (102/102), 63.38 KiB, done.
    Resolving deltas: 100% (45/45), completed with 18 local objects.
    From github.com:datafolklabs/boss-templates
       8626879..8bc867a  master     -> origin/master

You can add your own sources like so:

.. code-block:: text

    $ boss add-source my-remote git@github.com:john.doe/boss-templates.git
    
    $ boss add-source local /path/to/my/templates --local
    
The first example is a remote git repository that holds Boss templates.  The
second example is a local repository only, and will not attempt to sync with
a remote upstream repo.  At this time, Boss only support remote Git 
repositories.


Working with Templates
----------------------

Once your sources are in place, you can see what templates are available to
work with:

.. code-block:: text

    $ boss templates

    Local Templates
    ------------------------------------------------------------------------------
    python
    my-custom-template

    Boss Templates
    ------------------------------------------------------------------------------
    cement-script
    e2e
    license
    python


To create a new project, or part of a project, from a template do the 
following:

.. code-block:: text

    $ boss create ./helloworld -t local:python
    Version: [0.9.1] 
    Python Module Name: helloworld
    Python Class Prefix: HelloWorld
    Project Name: Hello World
    Project Description: Hello World does Amazing Things
    Project Creator: [BJ Dierkes] 
    Project Creator Email: [derks@bjdierkes.com] 
    License: [BSD-three-clause] 
    Project URL: http://helloworld.example.com
    ------------------------------------------------------------------------------
    Writing: /Volumes/Users/derks/helloworld/README
    Writing: /Volumes/Users/derks/helloworld/requirements.txt
    Writing: /Volumes/Users/derks/helloworld/setup.cfg
    Writing: /Volumes/Users/derks/helloworld/setup.py
    Writing: /Volumes/Users/derks/helloworld/helloworld/__init__.py
    Writing: /Volumes/Users/derks/helloworld/tests/test_helloworld.py
    Writing: /Volumes/Users/derks/helloworld/.gitignore
    Writing: /Volumes/Users/derks/helloworld/LICENSE
    

You'll notice a few things in this example:

Some questions were pre-populated by default answers.  These can be set under 
an '[answers]' config section in '~/.boss/config'.  For example:
 
.. code-block:: text

    [answers]
    creator = BJ Dierkes
    email = derks@bjdierkes.com
    version = 0.9.1
    license = BSD-three-clause


Also, as this is a python project template, the latest 'Python.gitignore' file 
was pulled down from http://github.com/github/gitignore and copied to 
.gitignore.

And it works:

.. code-block:: text

    $ python
    >>> import helloworld
    
With tests:

.. code-block:: text

    $ nosetests 
    test_helloworld (test_helloworld.HelloWorldTestCase) ... ok

    ----------------------------------------------------------------------
    Ran 1 test in 0.006s

    OK
