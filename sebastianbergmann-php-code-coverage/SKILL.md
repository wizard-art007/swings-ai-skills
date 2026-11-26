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

## Summary from README
phpunit/php-code-coverage provides collection, processing, and rendering functionality for PHP code coverage information.

## When to use
- When the task involves: UML diagrams.
- When you need to collect, process, or render PHP code coverage data programmatically.
- When generating reports (such as OpenClover) from live execution or serialized code coverage data.

## How to use
You can add this library via Composer:
```bash
composer require phpunit/php-code-coverage
```

### Collecting code coverage data and generating a report
```php
includeFiles( [
    '/path/to/file.php',
    '/path/to/another_file.php',
], );

$coverage = new CodeCoverage(
    (new DriverSelector)->forLineCoverage($filter),
    $filter,
);

$coverage->start('');
// ... execute code ...
$coverage->stop();

ReportFacade::fromObject($coverage)->renderOpenClover('/tmp/openclover.xml');
```

### Generating a report from serialized code coverage data
```php
$data = unserialize('/path/to/coverage.php');
ReportFacade::fromSerializedData($data)->renderOpenClover('/tmp/openclover.xml');
```

### Using existing scripts
- Run `python3 test_coverage_analyzer.py` to analyze existing test coverage workflows.

## Limitations
- Requires appropriate PHP extensions (such as Xdebug or PCOV) depending on the selected driver for code coverage collection.
- Performance overhead depends on the selected driver and the scope of the included files.