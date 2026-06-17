```markdown
# ai-video-shorts-generator Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you the development patterns and conventions used in the `ai-video-shorts-generator` Python repository. You'll learn how to structure files, write imports and exports, follow commit message conventions, and understand the project's basic testing approach. This guide is ideal for contributors aiming for consistency and maintainability in this codebase.

## Coding Conventions

### File Naming
- Use **snake_case** for all Python files.
  - Example: `video_processor.py`, `audio_utils.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .video_utils import process_video
    from .audio_utils import extract_audio
    ```

### Export Style
- Use **named exports** (explicitly listing what is exported).
  - Example:
    ```python
    __all__ = ["process_video", "extract_audio"]
    ```

### Commit Messages
- Follow the **Conventional Commits** style.
- Prefix commit messages with `feat`.
- Keep commit messages concise (average 55 characters).
  - Example:
    ```
    feat: add support for batch video processing
    ```

## Workflows

### Adding a New Feature
**Trigger:** When implementing a new functionality.
**Command:** `/add-feature`

1. Create a new Python file using snake_case if needed.
2. Implement the feature, using relative imports for dependencies.
3. Add named exports in the module's `__all__` list.
4. Write or update tests if applicable.
5. Commit your changes with a message starting with `feat:`.
   - Example: `feat: implement text-to-speech overlay`

### Refactoring Code
**Trigger:** When improving or restructuring existing code.
**Command:** `/refactor`

1. Identify the code to refactor.
2. Update file and function names to follow snake_case if necessary.
3. Adjust imports to use relative paths.
4. Update `__all__` lists as needed.
5. Commit with a descriptive message, e.g., `feat: refactor audio extraction logic`.

## Testing Patterns

- **Framework:** Unknown (not detected).
- **Test File Pattern:** Files end with `.test.ts`. (Note: This suggests some TypeScript tests, which may be legacy or for a different part of the project.)
- **Best Practice:** Place tests in files named like `module_name.test.ts` and ensure they cover new and changed functionality.

## Commands
| Command         | Purpose                                 |
|-----------------|-----------------------------------------|
| /add-feature    | Start workflow for adding a new feature |
| /refactor       | Start workflow for refactoring code     |
```
