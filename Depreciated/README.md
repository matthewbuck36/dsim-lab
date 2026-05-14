# Depreciated File Holding Area

This folder is the project-level holding area for files that would otherwise
be deleted during cleanup or renaming.

Rules for future AI/code-agent work:

- Do not hard-delete project files unless Matt explicitly asks for deletion.
- Move retired files here instead, grouped by date and reason.
- Preserve enough path context in the destination folder name or README note so
  the file can be recovered later.
- Prefer active code/config cleanup in the real source tree, and use this
  folder only for files that are no longer part of the active workflow.

Suggested layout:

```text
Depreciated/YYYY-MM-DD/<reason-or-area>/
```

Examples:

```text
Depreciated/2026-05-13/old_work_logs/
Depreciated/2026-05-13/duplicate_configs/
```

