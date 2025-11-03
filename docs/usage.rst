Usage
=====

Basic Usage
-----------

The simplest way to use txt-to-anki is to run it without any arguments:

.. code-block:: bash

   txt-to-anki

This will start the conversion process and output the results.

Command Line Options
---------------------

To see all available options:

.. code-block:: bash

   txt-to-anki --help

Examples
--------

Basic conversion:

.. code-block:: bash

   txt-to-anki

The tool will process your text and create Anki-compatible output.

Output
------

The tool will display progress information and completion status:

.. code-block:: text

   Converting text to Anki deck format...
   Conversion complete!

Troubleshooting
---------------

If you encounter issues:

1. Ensure you have Python 3.10 or higher installed
2. Verify the installation with ``txt-to-anki --help``
3. Check that all dependencies are properly installed

For development issues, ensure you're using Poetry and have run ``poetry install``.