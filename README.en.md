# Duo Kit

[简体中文](README.md) | **English**

**Let Codex plan and review, while Cursor focuses on implementation.**

Duo Kit is a lightweight toolkit for AI-assisted development on macOS. It consists of Bash scripts, agent instructions, and project templates. Task files define the scope, restricted areas, and acceptance criteria for each change, while project files and Git connect the work done in Codex and Cursor.

Use Codex directly for everyday work. When you want to split responsibilities, include `/duo` in your message and hand the resulting task file to Cursor.

> This is a file-based collaboration convention with manual handoffs between the two tools. The rules guide agent behavior; they do not enforce permission boundaries or automatically dispatch work.

## Why Duo Kit?

- **Collaborate when needed:** Codex handles tasks directly by default. Only messages containing `/duo` activate collaboration mode.
- **Define clear boundaries:** Each task file lists its goal, allowed files, restricted areas, and acceptance commands.
- **Keep handoffs traceable:** Plans, task states, and findings outside the task scope live in `.work/`, without requiring shared chat history.
- **Review after implementation:** Cursor runs its checks and marks the task ready for review. Codex inspects the changes and runs the acceptance commands itself.
- **Run setup again safely:** Global instructions are updated within a marked block, and project initialization skips existing files.

## Prerequisites

- macOS and Bash. The scripts use common Unix utilities; `pbcopy` copies rules to the clipboard.
- Working Codex and Cursor installations, installed and configured separately.
- Git is recommended for the target project so changes can be inspected with `git diff` during review.

The toolkit requires no additional package dependencies. macOS is the intended environment; compatibility with other operating systems has not been verified.

## Quick Start

### 1. Install the global rules

Download or clone this repository, then run the following from its `duo-kit` directory:

```bash
chmod +x bin/duo-install bin/duo-init
./bin/duo-install
```

The installer performs these actions:

| Location | Action |
| --- | --- |
| `~/.codex/AGENTS.md` | Adds or updates the `DUO-KIT` marked block, preserving content outside it |
| `~/.codex/prompts/duo.md` | Copies the command template if absent; skips existing files without overwriting them |
| System clipboard | Copies Cursor User Rules using `pbcopy`, or asks you to copy them manually if unavailable |

Open Cursor's rules settings and paste the rules into User Rules. You can also copy them manually from [global/cursor-user-rules.md](global/cursor-user-rules.md).

Add the toolkit's `bin` directory to PATH. Run this from the **duo-kit root directory**:

```bash
echo "export PATH=\"$(pwd)/bin:\$PATH\"" >> ~/.zshrc
source ~/.zshrc
command -v duo-init
```

The final command should print the path to `duo-init`. If you use another shell, update its configuration file instead. If you move the toolkit, update PATH accordingly.

### 2. Initialize your project

Go to the project you want to work on, rather than the toolkit directory:

```bash
cd /path/to/your/project
duo-init
```

Initialization creates:

```text
your-project/
├── AGENTS.md                  # Project rules shared by both tools
├── .cursor/
│   └── rules/
│       └── main.mdc            # Directs Cursor to follow project rules
└── .work/
    ├── plan.md                # Goals, architecture constraints, restrictions, progress
    ├── notes.md               # Findings outside the current task scope
    └── tasks/
        └── 000-template.md    # Task template
```

Fill in the project description, dependency installation, build, test, and lint commands, and coding conventions in `AGENTS.md`. Add your goals and architecture constraints to `.work/plan.md`.

**Existing files are skipped; rules are not merged automatically.** If your project already has `AGENTS.md` or `.cursor/rules/main.mdc`, compare them with [template/](template/) and merge the relevant content manually.

Commit these collaboration files to your project's version control to keep task history and handoffs traceable.

> The bundled agent rules, project templates, and script output are currently in Chinese. This English README explains their usage; it does not change the installed language. Keep the Chinese review/status keywords and task state labels shown below when following the bundled protocol.

## Two Working Modes

| Message to Codex | Behavior |
| --- | --- |
| `Help me fix the login failure` | Default mode: Codex edits code and runs tests directly, without creating task files |
| `/duo Add login functionality` | Collaboration mode: Codex plans and creates task files in `.work/tasks/` for Cursor to implement |
| `/duo 验收 003` | Codex reviews and verifies task 003 (`验收` means acceptance review) |
| `/duo 状态` | Codex summarizes task numbers, titles, and states, and suggests next steps (`状态` means status) |

Collaboration mode applies only to the current message containing `/duo`. Include the trigger explicitly in subsequent messages when needed.

### A Complete Workflow

**Step 1: Ask Codex to break down the work.** Send this in Codex:

```text
/duo Add request validation to the login endpoint, follow the existing API format, and add tests.
```

Codex reads the project rules, plan, and notes, then creates task files from the template. For example, `.work/tasks/001-login-validation.md` would define the allowed scope and executable acceptance commands.

**Step 2: Ask Cursor to implement the task.** Open the same project in Cursor and give its Agent the actual task file path:

```text
Execute .work/tasks/001-login-validation.md
```

Cursor sets the state to `进行中` (In progress), implements within the allowed scope, and runs the acceptance commands. Once they pass, it sets the state to `待验收` (Ready for review), records the changes and verification results, and adds findings outside the scope to `.work/notes.md`.

**Step 3: Ask Codex to review.** Return to Codex and send:

```text
/duo 验收 001
```

Codex checks `git diff`, file boundaries, and architecture constraints, and runs the acceptance commands itself. If they pass, it marks the task `完成` (Done) and updates the plan. Otherwise, it returns the task to `进行中` (In progress), records the issues, and you hand it back to Cursor for corrections.

```text
待办 (To do) → 进行中 (In progress) → 待验收 (Ready for review) → 完成 (Done)
                    ↑                       │
                    └──── Review fails ──────┘
```

Only Codex may mark a task Done after review. A separate branch or worktree per task is recommended to make the scope easier to inspect.

## Task File Convention

Use one file per task, named `NNN-short-name.md`, with sequential three-digit numbers. Use `000-template.md` as the template.

| Template field | What to include |
| --- | --- |
| `目标` — Goal | One small task with a clear, verifiable outcome |
| `允许改动文件` — Allowed files | Specific file paths or directories |
| `禁区` — Restricted areas | Files or behavior that must not be changed |
| `验收命令` — Acceptance commands | Commands that can be run directly, with clear pass criteria |
| `状态` — State | One of `待办`, `进行中`, `待验收`, or `完成` |
| `备注` — Notes | Implementation details, verification results, or reasons for returning the task |

See the full [task template](template/.work/tasks/000-template.md).

## Repository Structure

```text
duo-kit/
├── bin/
│   ├── duo-install            # Installs global rules and the command template
│   └── duo-init               # Copies project templates into the current directory
├── global/
│   ├── codex-AGENTS.md        # Codex default and collaboration mode rules
│   ├── cursor-user-rules.md   # Cursor implementation protocol
│   └── codex-prompts/
│       └── duo.md             # Optional Codex CLI custom prompt template
└── template/                  # Templates used to initialize projects
```

## Updating and Removing

After updating your local toolkit, run `./bin/duo-install` again to update the marked block in Codex's global instructions and copy the Cursor rules again. Replace the previously pasted Duo Kit rules in Cursor.

An existing `~/.codex/prompts/duo.md` will not be overwritten. To update it, back up any customizations, then merge manually or delete the file and rerun the installer. Existing project rules are not updated automatically either; compare them with `template/` and merge manually.

To remove the toolkit's configuration:

1. Remove the entire block from `<!-- DUO-KIT:BEGIN -->` through `<!-- DUO-KIT:END -->` in `~/.codex/AGENTS.md`, preserving other instructions.
2. Delete `~/.codex/prompts/duo.md` if it was installed by this toolkit, and remove the Duo Kit rules from Cursor User Rules.
3. Remove the added PATH line from your shell configuration.
4. Clean up project collaboration files as needed. Back up or manually merge existing project rules and task records first.

## FAQ

### Why is `duo-init` not found?

Make sure PATH points to the toolkit's actual `bin` directory and reload your shell configuration. You can also run `duo-init` using its absolute path while in your target project's directory.

### Why are collaboration rules missing after initialization?

`duo-init` skips every existing file with the same path. Check the output for skipped files and merge the templates manually. Running initialization again does not replace old rules.

### Must `/duo` be registered as a slash command?

The core convention is the `/duo` trigger in your message, interpreted through the installed agent instructions. The toolkit also includes a Codex CLI custom prompt template using `$ARGUMENTS` and attempts to install it at `~/.codex/prompts/duo.md`. Whether it appears as a menu command depends on your client and version.

Even without a corresponding command menu entry, you can type `/duo` followed by your request and ask Codex to follow the project rules.

### Do the tools call each other automatically?

No. You hand the task file path to Cursor, then return to Codex to request a review. Handoffs rely on `.work/` files and Git changes.

## Contributing

Issues and pull requests improving the scripts or templates are welcome. When reporting a problem, include your operating system, tool versions, commands, and relevant output, with sensitive information removed.
