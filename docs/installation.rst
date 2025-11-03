Installation
============

Requirements
------------

* Python 3.10 or higher
* pip or pipx

Using pipx (Recommended)
------------------------

pipx is the recommended way to install txt-to-anki as it creates an isolated environment:

.. code-block:: bash

   pipx install txt-to-anki

Using pip
---------

You can also install using pip:

.. code-block:: bash

   pip install txt-to-anki

Development Installation
------------------------

For development, clone the repository and use Poetry:

.. code-block:: bash

   git clone <repository-url>
   cd txt-to-anki
   poetry install

This will install all development dependencies including testing and documentation tools.

Verification
------------

Verify the installation by running:

.. code-block:: bash

   txt-to-anki --help

You should see the help message with available options.
