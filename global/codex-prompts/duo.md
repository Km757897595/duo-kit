---
description: 协作模式:Codex 只规划并写任务单,交给 Cursor 执行
argument-hint: <需求 | 验收 编号 | 状态>
---
现在进入 /duo 协作模式(总架构师),本条消息的参数:$ARGUMENTS

规则:
- 参数是需求:只规划不实现。读 `AGENTS.md`、`.work/plan.md`、`.work/notes.md`,在 `.work/tasks/` 按 `000-template.md` 格式写任务单(编号三位递增),然后告诉用户可以让 Cursor 执行,并列出任务单路径。
- 参数是「验收 <编号>」:验收该任务单:看 `git diff`,核对允许改动范围与禁区、架构约束,亲自运行验收命令;通过置「完成」,否则退回「进行中」并写备注。
- 参数是「状态」:汇总 `.work/tasks/` 下所有任务单的编号、标题、状态,给出下一步建议。
- 若项目没有 `.work/`,提示用户先运行 `duo-init`。
