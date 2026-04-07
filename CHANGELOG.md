# Changelog

All notable changes to the Smart Expense Tracker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup and structure
- Core project files and modules
- Database module for expense storage
- Analytics module for expense analysis
- Configuration management documentation
- Git Flow branching strategy implementation

### Changed
- Established branch protection rules for main branch
- Configured develop branch for integration testing

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

## [0.1.0-alpha] - 2026-04-07

### Added
- Initial project commit
- Smart Expense Tracker application structure
- Core modules: database, analytics
- Sample expense data
- Project documentation

### Changed
- Initial repository setup on GitHub

### Fixed
- None

---

## Version Details

### Upcoming: v1.0.0
- Target Release: End of semester
- Focus: Stable production release
- Status: In development on develop branch

### Current: v0.1.0-alpha
- Release Date: 2026-04-07
- Status: Initial release for configuration management assignment

---

## Guidelines for Contributors

When adding entries to this changelog:

1. Use the format: `[VERSION] - YYYY-MM-DD`
2. Group changes by category: Added, Changed, Deprecated, Removed, Fixed, Security
3. Include ticket/issue numbers when applicable
4. Keep entries clear and concise
5. Update this file in feature branches before merging

## Release Process

1. Update version in code
2. Update this CHANGELOG.md with all changes
3. Commit changes: `git commit -am "chore: release vX.Y.Z"`
4. Create Git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
5. Push tag: `git push origin vX.Y.Z`
