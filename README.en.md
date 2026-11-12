# Duo Kit

[简体中文](README.md) | **English**

**Let Codex plan and review, while Cursor or another Codex chat implements.**

Duo Kit is a lightweight toolkit for AI-assisted development on macOS. It consists of Bash scripts, agent instructions, and project templates. Task files define the scope, restricted areas, and acceptance criteria for each change, while project files and Git connect the work done in Codex and Cursor.

Use Codex directly for everyday work. When you want to split responsibilities, include `/duo` in your message and hand the resulting task file to Cursor or another Codex chat.

> This is a file-based collaboration convention with manual handoffs between the two tools. The rules guide agent behavior; they do not enforce permission boundaries or automatically dispatch work.

## Why Duo Kit?

- **Collaborate when needed:** Codex handles tasks directly by default. Only messages containing `/duo` activate collaboration mode.
- **Define clear boundaries:** Each task file lists its goal, allowed files, restricted areas, and acceptance commands.
- **Keep handoffs traceable:** Plans, task states, and findings outside the task scope live in `.work/`, without requiring shared chat history.
- **Review after implementation:** The implementer runs its checks and marks the task ready for review. Codex inspects the changes and runs the acceptance commands itself.
- **Let scripts keep the records:** Base commits, handoff HEAD, file SHA-256 hashes, and scope checks are recorded and verified by the `duo` command; agents never hand-write hashes.
- **Keep one copy of the protocol:** The protocol text lives only in the marked block of the project `AGENTS.md`; global rules just trigger collaboration and point to it.
- **Run setup again safely:** Global instructions are updated within a marked block, and project initialization skips existing files.

## Prerequisites

- macOS and Bash. The scripts use common Unix utilities; `pbcopy` copies rules to the clipboard.
- A working Codex installation. Install and configure Cursor separately if you want to use it for implementation.
- Git is recommended for the target project so changes can be inspected with `git diff` during review.

The toolkit requires no additional package dependencies. macOS is the intended environment; compatibility with other operating systems has not been verified.

## Quick Start

### 1. Install the global rules

Download or clone this repository, then run the following from its `duo-kit` directory:

```bash
chmod +x bin/duo bin/duo-install bin/duo-init
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

The final command should print the path to `duo-init`. If you use another shell, update its configuration file instead. If you move the toolkit, update PATH accordingly. During collaboration, the Codex and Cursor agents call the `duo` command, so make sure their terminals can find it too.

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
    ├── design.md              # UI design spec (for projects with a UI)
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
| `/duo Add login functionality` | Collaboration mode: Codex plans and creates task files in `.work/tasks/` for Cursor or another Codex chat to implement |
| `/duo 执行 003` | Codex implements task 003 and marks it ready for review after checks pass (`执行` means execute) |
| `/duo 验收 003` | Codex reviews and verifies task 003 (`验收` means acceptance review) |
| `/duo 状态` | Codex summarizes task numbers, titles, and states, and suggests next steps (`状态` means status) |

Collaboration mode applies only to the current message containing `/duo`. Include the trigger explicitly in subsequent messages when needed.

### A Complete Workflow

**Step 1: Ask Codex to break down the work.** Send this in Codex:

```text
/duo Add request validation to the login endpoint, follow the existing API format, and add tests.
```

Codex reads the project rules, plan, and notes, then creates task files from the template with `duo new`. For example, `.work/tasks/001-login-validation.md` would define the allowed scope, behavioral acceptance scenarios, and executable acceptance commands.

**Step 2: Ask Cursor or Codex to implement the task.** Open the same project in Cursor and give its Agent the actual task file path:

```text
Execute .work/tasks/001-login-validation.md
```

Alternatively, open the same project in another Codex chat and send:

```text
/duo 执行 001
```

The implementer first runs `duo start 001`, which records the base commit and pre-existing changes and sets the state to `进行中` (In progress). It then implements within the allowed scope, runs the acceptance commands, and checks each acceptance scenario. Once all checks pass, it runs `duo handoff 001`, which checks the scope, records the handoff code version, and sets the state to `待验收` (Ready for review). Findings outside the scope go in `.work/notes.md`.

**Step 3: Ask Codex to review.** Return to Codex and send:

```text
/duo 验收 001
```

Codex runs `duo check 001` to confirm the handoff code is unchanged and within scope, reviews the listed changes and architecture constraints, and runs the acceptance commands and verifies each scenario itself. If they pass, it marks the task `完成` (Done) and updates the plan. Otherwise, it returns the task to `进行中` (In progress), records the issues, and you hand it back to the implementer for corrections.

```text
待办 (To do) → 进行中 (In progress) → 待验收 (Ready for review) → 完成 (Done)
                    ↑                       │
                    └──── Review fails ──────┘
```

Only the architect may mark a task Done after review. The implementer must stop at Ready for review and must not review its own task during execution. A separate branch or worktree per task is recommended to make the scope easier to inspect.

## Task File Convention

Use one file per task, named `NNN-short-name.md`, with sequential three-digit numbers. Use `000-template.md` as the template.

| Template field | What to include |
| --- | --- |
| `目标` — Goal | One small task with a clear, verifiable outcome |
| `适用技能` — Skills | Optional; skill names and the step where each applies, read by the implementer before starting |
| `允许改动文件` — Allowed files | One path, directory, or glob per line, preferably in backticks; `duo` checks scope against it |
| `禁区` — Restricted areas | Paths in backticks are checked automatically; behavioral constraints are plain text |
| `验收场景` — Acceptance scenarios | Inputs or actions and observable expected results, covering normal, error, and relevant regression cases; UI tasks add a visual item |
| `验收命令` — Acceptance commands | Commands that can be run directly, with clear pass criteria |
| `代码版本` — Code version | Filled in automatically by `duo start` / `duo handoff`; do not edit by hand |
| `状态` — State | One of `待办`, `进行中`, `待验收`, or `完成` |
| `备注` — Notes | Implementation details, verification results, or reasons for returning the task |

See the full [task template](template/.work/tasks/000-template.md).

### Frontend Tasks and Skills

Passing builds and lint do not mean a page looks right or stays consistent. For projects with a UI:

- **One design direction**: before the first frontend task, the architect fills in `.work/design.md` (direction, colors and typography, component conventions, things to avoid). Every implementer follows it.
- **Named skills**: the task's `适用技能` field lists skill names and where they apply, such as `frontend-design` (aesthetic direction), `ui-ux-pro-max` (palettes and UX checks), or `hallmark` (new page design and design audits). The implementer reads them before starting; if the current tool cannot find one, it notes this and follows `design.md`.
- **Install and update**: Duo Kit does not bundle these skills. Manage them with the commands below (none of them touch project files):

  | Command | Purpose |
  | --- | --- |
  | `duo-init --skills frontend` | Checks whether recommended skills are installed and lists their locations; exits non-zero when any are missing |
  | `duo-init --skills frontend --install` | Installs missing skills globally for Codex and Cursor via `npx skills` (into `~/.agents/skills`); skips installed ones |
  | `duo-init --skills frontend --update` | Updates recommended skills via `npx skills update`; only skills installed by the `skills` tool are updated, others must be updated in the tool that manages them |

  Installing and updating require Node.js and fetch third-party skills from GitHub; review them before use.
- **Visual review**: the visual acceptance item names pages, viewports, and what to compare. The implementer saves browser screenshots to `.work/evidence/<number>/`, and the architect reviews them against `design.md`. Screenshots are records: they do not need to be listed in allowed files and are excluded from scope checks.

### The `duo` Record-Keeping Command

Run it from anywhere inside the project; it searches upward for `.work/tasks`.

| Command | Used by | Purpose |
| --- | --- | --- |
| `duo new <name>` | Architect | Allocates the next number and creates a task file from the template |
| `duo start <number>` | Implementer | Records working directory, branch, base commit, and pre-existing changes, and sets In progress; keeps the original base when resuming |
| `duo handoff <number>` | Implementer | Checks scope, records handoff HEAD, task commits, and SHA-256 of uncommitted files, and sets Ready for review; refuses out-of-scope changes |
| `duo check <number>` | Architect | Verifies state, working directory, branch, HEAD, and that files are unchanged since handoff, checks scope, and lists changes to review |
| `duo status` | Anyone | Summarizes all task states and suggests the next step |

- Snapshots are stored in `.work/snapshots/NNN-base.tsv` and `NNN-handoff.tsv`; commit them along with task files.
- Pre-existing changes that are unchanged at handoff are not attributed to the task; pre-existing files modified again by the task are attributed and scope-checked.
- Without Git or an initial commit, `duo` falls back to full file snapshots instead of commit diffs.
- `duo check` only guarantees that the handed-off code is what is there now and that it stays in scope; it does not replace code review or behavioral verification. Passing commands must also satisfy the acceptance scenarios. For a login validation task, check that missing passwords return the expected error and valid credentials still work, then record actual results. A successful build alone does not verify behavior.

## Repository Structure

```text
duo-kit/
├── bin/
│   ├── duo                    # Record keeping: new, start, handoff, check, status
│   ├── duo-common.sh          # Shared backup and rule update helpers
│   ├── duo-install            # Installs or updates global rules and the command template
│   └── duo-init               # Copies project templates into the current directory
├── global/
│   ├── codex-AGENTS.md        # Codex default mode and /duo trigger (points to project protocol)
│   ├── cursor-user-rules.md   # Cursor implementer trigger (points to project protocol)
│   └── codex-prompts/
│       └── duo.md             # Optional Codex CLI custom prompt template
└── template/                  # Project templates; the AGENTS.md marked block is the only protocol text
```

## Updating and Removing

After updating your local toolkit, run this from the toolkit directory:

```bash
./bin/duo-install --update
```

Then run this inside each target project:

```bash
duo-init --update
```

| Command | Behavior |
| --- | --- |
| `duo-install` | Updates the global `DUO-KIT` block; skips existing prompt files |
| `duo-install --update` | Updates the global block and backs up then replaces the existing `~/.codex/prompts/duo.md` |
| `duo-init` | Creates missing files; skips existing files |
| `duo-init --skills frontend [--install \| --update]` | Checks, installs, or updates recommended frontend skills; no project changes |
| `duo-init --update` | Updates the collaboration block in project `AGENTS.md`, backs up then replaces `.cursor/rules/main.mdc` and `.work/tasks/000-template.md`, and creates missing template files |

- Changed files are backed up alongside the originals as `filename.duo-backup.random-suffix`. Identical files are skipped without new backups. Restore manually from a backup if needed; backups may contain personal rules, so consider adding them to your project's `.gitignore`.
- Project descriptions, commands, and custom rules outside the managed block are preserved. Existing plans, notes, and actual task files under `.work/` are never overwritten. With `--update`, `000-template.md` is backed up and replaced as a whole file; merge custom template content manually from the backup. Identical content produces no new backup, and plain `duo-init` still preserves existing templates.
- Global rules only trigger collaboration and point to the project protocol. After upgrading, run `duo-init --update` in each project so its `AGENTS.md` gets the protocol that uses `duo`, and replace Cursor User Rules with the new short version. Tasks started by hand before the upgrade have no `.work/snapshots/` snapshot; `duo` refuses to hand them off, so the architect should confirm the current state and arrange a new handoff.
- After updating, the template contains the latest fields. Compare existing tasks with the [task template](template/.work/tasks/000-template.md) and manually add `验收场景` (Acceptance scenarios) and `代码版本` (Code version). If the historical base is unknown, record the current state and explicitly arrange a new handoff rather than inventing old records.
- For older projects without markers, the section titled `## 协作协议(架构师 + 突击手)` is replaced up to the next heading of the same or a higher level. Merge custom content from that section back from the backup. If no such section exists, the managed block is appended.
- Keep custom rules outside the managed block. Prompt files and Cursor project rules are replaced as whole files; manually merge their customizations from backups. Cursor User Rules still need to be pasted manually; the installer copies them to the clipboard.
- Unpaired or duplicate markers cause an error; the affected rule file is preserved. Repair its markers before retrying.
- All three scripts support `--help`. Updates use the local toolkit contents and do not fetch repository changes.

To remove the toolkit's configuration:

1. Remove the entire block from `<!-- DUO-KIT:BEGIN -->` through `<!-- DUO-KIT:END -->` in `~/.codex/AGENTS.md`, preserving other instructions.
2. Delete `~/.codex/prompts/duo.md` if it was installed by this toolkit, and remove the Duo Kit rules from Cursor User Rules.
3. Remove the added PATH line from your shell configuration.
4. Clean up project collaboration files as needed. Back up or manually merge existing project rules and task records first.

## FAQ

### Why is `duo-init` not found?

Make sure PATH points to the toolkit's actual `bin` directory and reload your shell configuration. You can also run `duo-init` using its absolute path while in your target project's directory.

### Why are collaboration rules missing after initialization?

`duo-init` skips every existing file with the same path. Use `duo-init --update` to update collaboration rules. Running initialization without that flag still skips existing files.

### Must `/duo` be registered as a slash command?

The core convention is the `/duo` trigger in your message, interpreted through the installed agent instructions. The toolkit also includes a Codex CLI custom prompt template using `$ARGUMENTS` and attempts to install it at `~/.codex/prompts/duo.md`. Whether it appears as a menu command depends on your client and version.

Even without a corresponding command menu entry, you can type `/duo` followed by your request and ask Codex to follow the project rules.

### Do the tools call each other automatically?

No. You hand the task file path to Cursor, or send `/duo 执行 <number>` in another Codex chat, then return to the architect chat for review. Handoffs rely on `.work/` files and Git changes.

## Contributing

Issues and pull requests improving the scripts or templates are welcome. When reporting a problem, include your operating system, tool versions, commands, and relevant output, with sensitive information removed.

## Development Checks

Integration tests use a temporary HOME, temporary projects, and an isolated clipboard command, without changing your real Codex configuration:

```bash
python3 -m unittest discover -s tests -v
bash -n bin/duo bin/duo-install bin/duo-init bin/duo-common.sh
```
