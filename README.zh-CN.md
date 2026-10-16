# Agent Memory Template

用 Markdown 和 Git，让不同编程 agent、不同机器共享长期记忆。
每个项目一个目录，`MEMORY.md` 保存索引，每条事实单独一个文件。

[English](README.md) · [共享协议](PROTOCOL.md) · [虚构示例](examples/my-app)

这个公开模板只包含虚构示例。**保存真实记忆时，请创建自己的私有仓库。**
不需要 API key、数据库或模型服务。辅助脚本适用于 macOS / Linux，
需要 Python 3.9+、Bash 和 Git。

## 开始使用

1. 在 GitHub 点 **Use this template → Create a new repository**，选择
   **Private**，仓库名可以用 `agent-memory`。
2. 克隆你刚创建的仓库。下面的 URL 需要替换为自己的地址：

   ```bash
   git clone YOUR_PRIVATE_REPOSITORY_URL "$HOME/.agents/memory"
   cd "$HOME/.agents/memory"
   ```

   也可以使用其他空目录。安装器会采用当前仓库的实际绝对路径。
   已有记忆库时，请先用另一个目录，手动核对迁移内容。
3. 把 `my-app` 改成项目目录名，先预览，再安装：

   ```bash
   python3 bin/install.py --project my-app \
     --instructions "$HOME/.codex/AGENTS.md" \
     --instructions "$HOME/.claude/CLAUDE.md" --dry-run

   python3 bin/install.py --project my-app \
     --instructions "$HOME/.codex/AGENTS.md" \
     --instructions "$HOME/.claude/CLAUDE.md"
   ```

   不使用的 agent 可以去掉对应参数。安装器保留原有指令，只更新带标记的
   协议段落；重复运行不会重复追加。项目初始索引为空，不会导入示例。
4. 按 [agent 接入说明](README.md#connect-your-agents)配置访问权限，
   重新开启会话，先确认 agent 找到了正确的记忆目录，再尝试保存一条偏好。

Codex 使用自定义 `CODEX_HOME` 或 `AGENTS.override.md` 时，需要传入实际生效的
指令文件。`workspace-write` 会话还需允许访问记忆目录；安装器不会修改权限。
Claude Code 可以把项目的 `.claude/settings.local.json` 中
`autoMemoryDirectory` 指向同一个项目记忆目录，注意保留原有设置。

## 保存什么

| 类型 | 适合保存的内容 |
| --- | --- |
| `user` | 稳定偏好、与工作有关的背景 |
| `feedback` | 纠正过的问题、原因和以后如何处理 |
| `project` | 无法从代码推断的产品或团队背景 |
| `reference` | 外部资料的入口及核实时间 |

不保存临时进度、会话全文、源码摘要、凭据或私有文档副本。
事实会过时，当前用户指令和核实后的证据优先。
记忆写入仍需遵守用户与当前会话的授权规则。

项目按目录名匹配，也会向上寻找已启用的父目录。同名项目会共用记忆，
不同目录名的 worktree 则不会自动归到同一个项目；这两种情况都可以在用户级
指令里明确映射。新增项目只需运行：

```bash
python3 bin/install.py --project another-app
```

## 多机器同步

每台机器克隆自己的私有记忆仓库，并分别安装协议。开始前运行
`bash bin/sync.sh pull`。结束后检查改动和新增文件，手动 `git add`、
`git commit`，再运行 `bash bin/sync.sh push`。

脚本不会自动提交、强制推送或改写历史。工作区有改动、未设置 upstream、
分支分叉时会报错，交给你检查处理。它不安装自动执行的 hooks，Git 认证可能
需要交互。多个 agent 同时修改文件仍需人工检查冲突。

完整同步命令、迁移、断开接入及限制见 [英文说明](README.md)。
本模板采用 MIT License；个人记忆库的访问权限由其所有者决定。
