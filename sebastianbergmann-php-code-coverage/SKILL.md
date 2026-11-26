---
name: sebastianbergmann-php-code-coverage
description: Library that provides collection, processing, and rendering functionality for PHP code coverage information.
source: https://github.com/sebastianbergmann/php-code-coverage
license: BSD-3-Clause
stars: 8922
language: PHP
topics: 
saved: 2026-11-26
---

# sebastianbergmann/php-code-coverage

Use this skill when the task involves: UML diagrams.

- Source code: cloned on demand (`ensure_repo(skill)`); licence file(s): see source
- Original README: `README_source.md`

## Summary from README
# phpunit/php-code-coverage [](https://packagist.org/packages/phpunit/php-code-coverage) [](https://github.com/sebastianbergmann/php-code-coverage/actions) [](https://codecov.io/gh/sebastianbergmann/php-code-coverage) Provides collection, processing, and rendering functionality for PHP code coverage information. ## Installation You can add this library as a local, per-project dependency to your project using [Composer](https://getcomposer.org/): ``` composer require phpunit/php-code-coverage ``` If you only need this library during development, for instance to run your project's test suite, then you should add it as a development-time dependency: ``` composer require --dev phpunit/php-code-coverage ``` ## Usage ### Collecting code coverage data and generating a report ```php includeFiles( [ '/path/to/file.php', '/path/to/another_file.php', ], ); $coverage = new CodeCoverage( (new DriverSelector)->forLineCoverage($filter), $filter, ); $coverage->start(''); // ... $coverage->stop(); ReportFacade::fromObject($coverage)->renderOpenClover('/tmp/openclover.xml'); ``` ### Generating a report from serialized code coverage data ```php unserialize('/path/to/coverage.php'); ReportFacade::fromSerializedData($data)->renderOpenClover('/tmp/openclover.xml'); ```
