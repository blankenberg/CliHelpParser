Changelog
=========
0.2.0 (2020-05-25)
------------------
Features
********
* Add ``parameter_meta`` (parameter documentation) generation back into WDL definitions
* Add :py:meth:`acclimatise.model.Command.depth`, and :py:attribute:`acclimatise.model.Command.parent` to :py:class:`acclimatise.model.Command` to facilitate the traversal of the command tree
* Add ``dinosaur`` and ``mauveAligner`` as test cases in ``test/test_data``
* Convert tests into a series of test case objects that can be used to parameterize each test function
* Add the option to parallelize tests using pytest-parallel
* Better conversion of symbols to variable names, for example "/" is now "slash" rather than "solidus"
* Add logging to the high level functions like ``explore_command``, using the ``acclimatise`` logger. This should make
tracking errors and progress a tad easier.
* By default, re-use the best help command from the parent on the child. For example if we determine that
``samtools --help`` is the most accurate help command for ``samtools``, then we use ``samtools sort --help`` without
having to test out every possible flag here
* Add ``generated_using`` field to the ``Command`` class, which tracks the flag used to generate it

Changes
*******
* Set the default command depth to 3
* ``aCLImatise`` now only supports Python >= 3.7.5, due to `this bug <https://bugs.python.org/issue37424>`_

Fixes
*****
* Avoid variable naming collisions using a generator-based iteration method in ``acclimatise.name_generation.generate_names``
* Keep a global ``spacy`` instance to minimize memory footprint. This is available in :py:module:`acclimatise.nlp`
* Fix infinite loops in explore, e.g. tools like ``dinosaur`` and ``mauve`` by adding more advanced subcommand detection in ``acclimatise.is_subcommand``
* Make cmd optional for validators
* Always run commands in a pseudo-TTY so that commands like ``samtools`` will output help
* Various other fixes

0.1.5 (2020-05-18)
------------------
* Bugfix for when we have no help text
* Add a test for a program that we know fails

0.1.4 (2020-05-18)
------------------
* Choose best command using length of help text, if everything else is equal

0.1.3 (2020-05-15)
------------------
* ``Command`` types now contain a ``help_text`` field which records the string that was used to generate them. This should enable efficient re-parsing, and can also be displayed downstream by BaseCamp
* Rewrite tests into a parametrized, consolidated end-to-end test
* Fix "OPTIONS" being considered a positional argument, when really it's a placeholder for flags
* Remove positional arguments that precede the main command, so `dotnet Pisces.dll` will be removed from the entire
command

0.1.2 (2020-05-15)
------------------
* Generating YAML output now produces one file for each subcommand, to match other converters

0.1.1 (2020-05-13)
------------------
* Make ``explore -o`` flag default to current working directory, for simplicity
* Updated the readme
* Add installation instructions

0.1.0 (2020-05-13)
------------------
* Fix the doubled variable names like ``bytesBytes``
* Smarter POS-based algorithm for generating names from descriptions
* Automatically choose a description based name when we have only short named flags like ``-n``
* Add changelog
* Add comprehensive testing for CWL and WDL generation
* Fix for variable names with symbols in them
* Use regex library for faster and more concise regex
