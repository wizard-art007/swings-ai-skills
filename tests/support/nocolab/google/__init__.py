# Test-only shim: makes `import google.colab` fail inside the test suites, so the engine never believes it runs in
# Colab (where it would use the real Drive folder). Every other google.* package is still found normally.
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
