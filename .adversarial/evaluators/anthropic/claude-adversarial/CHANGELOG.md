# Changelog

All notable changes to the claude-adversarial evaluator will be documented in this file.

## [1.0.0] - 2026-02-02

### Added

- Initial release of Claude 4 Opus adversarial evaluator
- Adversarial review prompt adapted from gpt52-reasoning
- Standardized output format with severity labels (CRITICAL/HIGH/MEDIUM/LOW)
- Support for ANTHROPIC_API_KEY environment variable
- 180-second timeout (standard category)

### Notes

- Part of AEL-0005: Phase 1 Evaluator Implementation
- Provides Anthropic coverage for adversarial category
