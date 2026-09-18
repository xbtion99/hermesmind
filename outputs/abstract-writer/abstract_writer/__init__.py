"""abstract_writer — writes abstract prose that earns its abstraction.

Public entry points:
    abstract_writer.pipeline.write(seed, provider, options) -> Result
    abstract_writer.lint.lint_text(text, lang) -> LintReport
    abstract_writer.providers.make_provider(name, ...) -> Provider
"""

__version__ = "0.1.0"
