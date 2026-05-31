# OpenCode `external_directory` Permission Guide

The `external_directory` permission is a safety guard triggered whenever a tool (such as `read`, `edit`, `glob`, `grep`, or `bash`) attempts to access a file or directory outside the working directory where OpenCode was started.

## 🛠️ Correct Syntax

To allow access to a project directory and all its subdirectories, use the **recursive glob pattern (`**`)** within the `permission.external_directory` object in your `opencode.json`.

### Recommended Configuration
```json
{
  "permission": {
    "external_directory": {
      "~/path/to/your/project/**": "allow"
    }
  }
}
```

### Key Syntax Rules
- **Recursive Access**: Use `**` at the end of the path to grant access to the directory and every nested file/folder.
- **Home Expansion**: You can use `~` or `$HOME` at the start of the pattern to reference your home directory (e.g., `~/Documents/code/**`).
- **Absolute Paths**: For directories outside the home folder, use full absolute paths (e.g., `/mnt/data/projects/**`).

---

## 🔍 Troubleshooting "Access Denied" Errors

If you have configured the whitelist but still encounter "Access denied" errors, check for these common causes:

### 1. Tool-Specific Overrides
`external_directory` is a general gate. However, specific tools can have their own rules that override the general allowance. 
**Example**: If you allow the directory in `external_directory` but have a global `deny` for the `edit` tool, you will be able to read files but not modify them.
```json
"permission": {
  "external_directory": { "~/my-project/**": "allow" },
  "edit": { "~/my-project/**": "deny" } // This will block edits despite the whitelist
}
```

### 2. "Last Match Wins" Logic
OpenCode evaluates rules in order; **the last matching rule takes precedence**. If you have a broad `deny` rule appearing after your specific `allow` rule, the access will be blocked.
**Wrong**:
```json
"external_directory": {
  "~/projects/secret/**": "allow",
  "*": "deny" // This catch-all wins and blocks the secret project
}
```
**Right**:
```json
"external_directory": {
  "*": "deny",
  "~/projects/secret/**": "allow" // Specific rule wins
}
```

### 3. Pattern Mismatch (Globbing)
- **Missing `**`**: Using `~/project/*` only matches files in the top level of that folder. It does **not** match subdirectories. Always use `**` for recursive project access.
- **Relative Paths**: `external_directory` rules are intended for paths *outside* the workspace. Using relative paths (like `../other-folder/**`) can be unreliable; always use absolute paths or `~`/`$HOME`.

### 4. Default State
By default, `external_directory` is set to `"ask"`. If you haven't explicitly set it to `"allow"`, OpenCode will prompt you for approval. If the prompt is suppressed or rejected, it results in an "Access denied" state.

## ✅ Summary Checklist
- [ ] Does the path start with `~`, `$HOME`, or `/`?
- [ ] Does the pattern end with `**` for recursive access?
- [ ] Is the `allow` rule placed **after** any broader `deny` rules?
- [ ] Have you checked if the specific tool (e.g., `edit`, `bash`) is blocked separately for that path?
