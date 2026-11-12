---
description: 协作模式:Codex 规划、执行已有任务单或验收
argument-hint: <需求 | 执行 编号 | 验收 编号 | 状态>
---
现在进入 /duo 协作模式,参数:$ARGUMENTS

读项目根目录 `AGENTS.md` 中 `DUO-KIT` 标记块内的协作协议,按参数选择角色与流程:优先匹配「执行 <编号>」「验收 <编号>」「状态」子命令,其余参数作为新需求;执行或验收缺少编号时先澄清。项目没有 `.work/` 时提示运行 `duo-init`,没有协议块时提示运行 `duo-init --update`。
