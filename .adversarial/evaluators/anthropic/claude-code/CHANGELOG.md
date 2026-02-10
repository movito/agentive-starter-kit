# Changelog

All notable changes to the claude-code evaluator will be documented in this file.

## [1.0.0] - 2026-02-02

### Added

- Initial release of Claude 4 Sonnet code review evaluator
- Security-focused prompt adapted from o1-code-review
- Checks for injection, XSS, path traversal, hardcoded secrets
- Standardized output format with severity labels (CRITICAL/HIGH/MEDIUM/LOW)
- Support for ANTHROPIC_API_KEY environment variable
- 180-second timeout (standard category)

### Notes

- Part of AEL-0005: Phase 1 Evaluator Implementation
- Provides Tier 1 Anthropic coverage for code-review category
