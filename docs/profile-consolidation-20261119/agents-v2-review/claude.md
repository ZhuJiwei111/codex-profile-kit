# 复审结论：可接受，无阻塞问题

本次引入的改动衔接成立，没有发现新的冲突或悬空引用：

- **worktree 分层清楚**：AGENTS 管授权，multiline 管流程，subagent 只做边界引用。
- **锚点有效**：`#worktree-selection-and-creation` 与标题一致。
- **记录规则一致**：journal 的“只读任务不写记录 / 已有写入授权内按需初始化”与全局完全对应。
- **旧规则已清除**：未见 Goal 固定推荐或暂停引用规则的残留。
- **重复可接受**：multiline 的“Reuse confirmation only for that same worktree”与全局略有重复，但它补充了“默认位置或他任务批准不算确认”，属于流程细化，不需要删。

## 可选修订（均为旧问题，不阻塞）

**1. multiline 中任务属主的提交措辞**
- 引文：`Task owners independently implement, execute, repair, validate, document, commit and close within the original task authority.`
- 场景：经 multiline 新建的代码任务属主，可能把 “commit” 理解为默认职责，而全局规定提交须另有授权。后文 `Where the user grants standing commit…` 已有限定，但相隔较远。
- 最小修订：把 `commit` 改为 `commit when authorized`。

**2. profile-sync 的触发条件过窄**
- 引文：`Manual only. Use only when the user explicitly invokes this skill`
- 场景：用户只说“修改并部署 profile”，没有点名该 skill。agent 可能判断不能触发它，转而手工复制文件，绕过 backup、drift 检查和 `check`。这与全局“安装副本沿已有流程更新”相背。
- 最小修订：在 description 中补上 `or explicitly requests portable-profile preview/apply/check/deploy`，仍保持仅在显式请求时使用。

**3. 自主委派的口径（极轻）**
- 全局写的是“明确要求委派时…”，subagent 写的是 `or when an independent bounded line materially improves…within existing delegation authority`。
- 两者并不冲突，因为全局只覆盖显式请求的情形。若不想留解读空间，可在全局补“或在已有委派授权内自主委派”。不改也可以。

## 场景回放

1. **只授权新会话，未确认 worktree**：创建会话不等于授权 worktree，优先选用合适的已有目录，用已有目录无需审批。如确需新建，先给出用途、仓库和完整路径，一并询问“是否创建”和“位置”。如果 `create_thread` 自带建 worktree 选项，不启用。✓
2. **已确认创建，未确认位置**：只询问位置，并给出拟用完整路径。默认位置不算确认。工具无法使用约定路径时，把位置选择交回用户，不静默换路径。✓
3. **同一 worktree 两项均已确认**：不重复询问，用 `create_worktree` 创建，再把会话绑定到实际返回的路径。若是委派 worker，直接传入已确认的目录；缺少的 worktree 决定退回派发任务。✓
4. **只读审阅**：只检查和分析，不改文件，不写日志，不初始化记录。最终答复以“下一步建议”结尾。✓
5. **授权修改并部署 profile**：
   - 在 portable 源中修改，先比对 active 与源的既有差异；
   - 用 `--path` 做 scoped 的 preview、apply、check；
   - 不提交，因为 profile-sync 写明“do not commit merely to deploy”，全局也要求提交另行授权；
   - 汇报实质规则变化、backup 路径和检查结果，并区分“已部署”与“未提交/未发布”。
   
   唯一的衔接隐患是发现 2 中的触发措辞。✓

下一步建议：可选地对 multiline 和 profile-sync 各做一处单词级修订（发现 1、2），其余保持现状。
