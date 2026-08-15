# 长任务监督的社区方案与折中设计（2026-08-15）

## 结论先行

有比“让 agent 持续轮询”和“完全无人监督”都更好的办法，但它不是某个更聪明的 prompt，而是把等待与判断拆开：

1. 由不调用模型的 runner/supervisor 持有进程、退出码、timeout、heartbeat、日志和 checkpoint。
2. 正常运行时只在宿主侧等待或做廉价检查，不向对话写入 heartbeat，也不产生 model turn。
3. 只在 `completed`、`failed`、`timed_out`、`watchdog_stalled` 或 `needs_input` 等状态跃迁时，向人或 agent 投递一次有界的 attention event。
4. agent 被唤醒后先读取结构化结果和有限日志尾部，只有证据不足时才扩大检查；处置权限仍由原任务授权决定。

可以把这个模式概括为：**事件驱动为主、宿主 watchdog 兜底、模型只在需要判断时介入**。成熟的 systemd、Slurm 和 GitHub Actions 都沿用这一职责划分；Claude Code 已经出现了相当直接的 agent-side 实现。Codex 的协议也有大部分拼图，但截至本次调研，Codex Desktop 的 `Stop` continuation 仍不适合被当成唯一可靠唤醒通道。

对当前使用方式最重要的判断是：

- `/goal` 适合“agent 每一轮都能继续做有效工作”的迁移、修复、实验迭代和验证闭环。
- 对一个已经启动、接下来几十分钟或数小时没有可操作空间的训练、构建或远程 job，继续让 `/goal` 或普通 turn 检查状态通常没有价值。应把等待移出 agent。
- 完全不监督也不是必要代价。进程退出、timeout、heartbeat 停滞和已知 fatal pattern 都可以由零 token 的宿主程序及时发现。
- 在 Codex Desktop 上，应把系统通知或其他人类可见通知保留为可靠 fallback；自动恢复同一 task 只能在具体 App/CLI 版本通过 sentinel 验收后视为 best-effort 加速通道。

## 调研范围与证据边界

本文只采用产品官方文档、上游源码/手册、官方仓库 issue，以及被点名的开源实现作为主要证据。下面用“事实”表示来源明确写出的行为；用“推断”表示基于多个系统共同设计模式得出的建议。

一个重要的证据边界是：OpenAI 官方 `/goal` 文档说明其用途、控制方式和结果合同，但没有公开 Codex Goal 内部以何种频率发起模型调用。因此，不能从官方文档断言 Codex `/goal` 一定采用某种固定轮询算法。本文关于轮询造成 token 与上下文负担的讨论，一部分来自用户观察，另一部分由 Claude Code 明确公开的 evaluator/loop 机制作为可比证据支持。

## 1. OpenAI Codex：Goal、Hooks 与通知各自解决什么

### 1.1 Goal 适合持续推进，不是理想的被动进程 watcher

OpenAI 将 `/goal` 定义为跨多个 turn 追踪一个可验证停止条件的长任务模式。官方建议目标包含 outcome、constraints、verification，按 checkpoint 工作并保留短 progress log；Goal 可以独立工作多小时，并在达到停止条件时结束。[Follow a goal](https://learn.chatgpt.com/use-cases/follow-goals) [Long-running work](https://learn.chatgpt.com/docs/long-running-work)

官方还建议用 side chat 获取状态、在可能失去连接前暂停 Goal，以及用系统通知查看 task 是否需要输入或已可审阅。Goal 不会扩大 sandbox、approval 或原有权限。[Long-running work](https://learn.chatgpt.com/docs/long-running-work)

事实并不等于“Goal 等待是免费的”：上述文档没有说明内部 model-turn cadence、token 成本或被动命令等待时的优化策略。因此更稳妥的结论是：

- 对“修复一个失败后立即能做下一步”的 agentic loop，Goal 是原生且合适的控制面。
- 对“训练进程运行两小时，在退出前没有任何可做动作”的阶段，Goal 的持续上下文没有带来相称收益；用外部 supervisor 等待更符合职责分离。

### 1.2 Codex Hooks 已具备事件输入与有界上下文，但后台 hook 不会主动开 turn

Codex Hooks 是在 lifecycle event 上运行确定性脚本的扩展框架。官方列出的用途包括日志、验证和持久化摘要；多个匹配 command hook 会并发运行，非托管 hook 需要 trust review。[Hooks](https://learn.chatgpt.com/docs/hooks)

与本问题直接相关的协议事实是：

- `Stop` 返回 `{"decision":"block","reason":"..."}` 时，协议规定 Codex 应继续并自动创建一个以 `reason` 为文本的新 user-like continuation prompt。
- `stop_hook_active` 表示该 turn 是否已经由 `Stop` 继续过，可用于防止无限循环。
- `UserPromptSubmit` 可以在用户下一次发消息时注入 `additionalContext`，因此天然适合作为“漏掉自动唤醒后的交互恢复”通道，而不是无人值守唤醒。
- command hook 可以设置 `async: true`。但后台 hook 完成时，如果当前没有活跃 turn，输出会等到下一次用户 turn；“完成后台 hook”本身不会启动新 turn。后台 hook也不能 block、approve、rewrite 或控制原操作，session 结束时未完成的后台 hook 会被取消且未交付输出会丢弃。

这些行为见 [Codex Hooks 官方文档](https://learn.chatgpt.com/docs/hooks)。它们说明 Codex 已经有“后台执行”和“继续 turn”两个组件，但当前官方后台 hook 并没有一个独立于 `Stop` 的可靠 idle re-wake seam。

### 1.3 日志外置与 context cap 已是官方推荐方向

Codex 默认把每个 model-visible hook output 限制在约 2,500 tokens；更大的输出会写入临时文件，只把 head/tail preview 和路径交给模型。官方明确提醒多个 hook/plugin 的 context 会累加并降低模型表现，不应无界提高 `additionalContextLimit`。[Hooks: Large hook output](https://learn.chatgpt.com/docs/hooks#large-hook-output)

这直接支持一个重要设计原则：完整日志应在磁盘或调度器中，conversation 只接收稳定、短小、去重的 result envelope。让每次 heartbeat 或日志增量进入对话，即使不产生很多推理 token，也会污染后续判断所依赖的上下文。

社区报告与研究也给出了成本方向上的证据。openai/codex [#13733](https://github.com/openai/codex/issues/13733) 报告后台进程轮询会触发携带历史的完整 API turn；[#35259](https://github.com/openai/codex/issues/35259) 在一个本地观测窗口中把 wait/status-only turns 估算为原始 token 量的 19.8%。这两个数字都是 issue 作者的特定环境测量，不应外推成产品基准。更一般地，[SentinelBench](https://arxiv.org/abs/2606.05342) 的实验比较显示：用 `sleep` 轮询时，成功任务的成本随等待时长增长；改用事件式 `wait_for` 后，成本对等待时长相对稳定。这支持“等待本身不应生成模型 turn”，但不证明任一现有 Codex 版本已经实现该原语。

### 1.4 Codex 原生“等待而不耗 token、事件到达再唤醒”仍是能力缺口

截至本次调研，openai/codex 中与这个缺口直接相关的条目仍以 feature request / issue 形式存在，而不是已发布、可依赖的产品合同：

- [#28144](https://github.com/openai/codex/issues/28144) 请求为 Goal 增加持久化的 wait/wake 状态：等待期间不发 model turn，之后可由 timer、外部事件、用户或 App Server 唤醒。
- [#29922](https://github.com/openai/codex/issues/29922) 提议 agent 可调用的 `monitor` 工具：watcher 安静时不发生 API 调用，stdout/stderr 事件才唤醒空闲 session。该 issue 提到的 fork/reference implementation 不是已合入 Codex 的行为。
- [#32188](https://github.com/openai/codex/issues/32188) 是同一问题簇中关于后台 exec 完成后事件驱动通知/唤醒的开放讨论。

这些条目是社区报告或设计提议，不能反过来证明 Codex 的每个 Goal 都必然用高频轮询；它们能支持的较窄结论是：截至 2026-08-15，官方文档没有给出一个可依赖的、通用的 idle-task event re-wake 原语，相关需求仍未形成稳定公开合同。

### 1.5 Codex Desktop `Stop` continuation 的现实可靠性

官方协议说 `Stop decision:block` 会创建 continuation；但是 openai/codex 官方仓库中截至本次调研仍可见多条相关未关闭报告：

- [#33992](https://github.com/openai/codex/issues/33992)：Codex Desktop 上最小 `Stop decision:block` reproduction 触发内部 `ApiIdParam` 错误，期望的 continuation 未正常交给 agent。
- [#20783](https://github.com/openai/codex/issues/20783)：blocking Stop hook 生成的 continuation 在下一次 Responses 请求中因本地 message id 格式被拒绝。
- [#21160](https://github.com/openai/codex/issues/21160)：报告 rate-limit stop 或 live `hooks.json` 修改后 hooks 不再触发，重启 session 才恢复。
- [#22858](https://github.com/openai/codex/issues/22858)：报告用户用 Esc 中断 turn 时 `Stop` 不触发，外部状态可能永久停在 running。

这些是用户提交的 issue，不是“所有版本必现”的官方声明，也不能证明每个当前构建都失败；但它们足以否定“把 Stop continuation 当成唯一 durable notification channel”的工程假设。尤其对无人值守任务，silent miss 比显式失败更危险。

### 1.6 人类通知是可靠但不自动处置的 fallback

ChatGPT/Codex Desktop 可以在 turn 完成、需要权限或需要回答时发系统通知，Activity view 也能显示 Running、Needs input、Ready、Blocked 等状态；CLI/IDE 可以配置外部通知程序。[Notifications](https://learn.chatgpt.com/docs/notifications)

它不能让 agent 自动诊断任务，但能显著缩短“完全无人监督”时的人工发现延迟。因此在自动 continuation 尚不可靠时，“宿主事件 -> 系统通知 -> 用户点回同一 task”是合理的可靠基线，而不是退回手工盯日志。

## 2. Anthropic Claude Code：社区中最接近理想折中的现成协议

Claude Code 的当前官方文档把轮询成本与事件驱动方案说明得更直接，可以作为 Codex 方案设计的对照，而不是 Codex 行为的保证。**本节所有 `/goal`、Monitor 和 `asyncRewake` 行为都只属于 Anthropic Claude Code；它们不是 OpenAI Codex `/goal` 或 Hooks 的功能说明。**

### 2.1 `/goal` 明确是每 turn evaluator

Claude Code `/goal` 是 session-scoped prompt-based `Stop` hook。每个 agent turn 完成后，一个小模型根据已有对话判断目标是 `not yet met`、`met` 还是 `impossible`；它不能自行读文件或运行命令，evaluation tokens 会计费，状态页会显示 turn 数和 token spend。[Claude Code `/goal`](https://code.claude.com/docs/en/goal)

这准确展示了 Goal 类监督的优势与成本：它非常适合每一轮都有新证据和新动作的工作，但把“等待外部进程”实现成反复 turn/evaluation，会重复消费 token，并要求足够证据进入 transcript。

### 2.2 `asyncRewake` 是本问题所需 seam 的直接实现

Claude Code command hook 除了普通 `async`，还有 `asyncRewake: true`：hook 在后台运行，退出码为 2 时会立即唤醒空闲 Claude，并把 stderr（或 stdout fallback）作为 system reminder 交给模型。普通 async hook 在 session 空闲时仍等到下一次用户交互；`asyncRewake` 是官方列出的例外。[Claude Code Hooks](https://code.claude.com/docs/en/hooks#run-hooks-in-the-background)

这个机制的价值在于：

- watcher 等待期间没有 model turn；
- 真正 attention event 到来时能立即让模型处理；
- watchdog 逻辑是普通本地程序，可以廉价高频检查，而不会把每次检查写进对话。

局限也很明确：每次 hook firing 会生成独立后台进程且没有自动去重；非交互 `-p` teardown 会杀掉未完成 async hook，除非 hook 自己启动完全 detached process；hook 仍受 session 生命周期和 trust 边界影响。它说明“这个协议形态可行”，不代表它已经在 Codex 中存在。

### 2.3 Monitor 比 prompt loop 更省，但必须抑制正常输出

Claude `/loop` 可以固定间隔或动态选择 1 分钟至 1 小时的间隔。官方明确说动态 loop 可改用 Monitor：后台脚本把输出行推入 session，避免重复 prompt polling，通常更省 token且反应更快。[Claude Code scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)

但 plugin monitor 会把**每一行 stdout**都作为 notification 交给 Claude；它只在交互式 CLI session 中运行，session 结束时停止，而且 background Bash/monitor 不会在 resume 后恢复。[Claude Code plugin monitors](https://code.claude.com/docs/en/plugins-reference#monitors) [Claude Code scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks)

因此事件驱动并不自动等于低污染：monitor 必须只在状态跃迁或异常时输出，heartbeat 应写到外部状态文件而不是 stdout。Claude Agent SDK 的 `TaskNotificationMessage` 也体现了同一设计：background task 只在 `completed`、`failed` 或 `stopped` 时发包含 `output_file` 和短 `summary` 的完成消息。[Claude Agent SDK Python reference](https://code.claude.com/docs/en/agent-sdk/python)

## 3. `codex-defer-and-resume`：方向正确，但受 Codex 最后一跳限制

[zibo-chen/codex-defer-and-resume](https://github.com/zibo-chen/codex-defer-and-resume) 是一个非官方实验性 Codex Skill + Stop Hook。其核心做法是：detached Python worker 执行命令并把 stdout/stderr 写入 `output.log`，把结构化状态写入 `result.json`；Stop hook 在本地轮询状态，不调用模型，看到完成后用 `decision:block` 恢复同一个 task。[README](https://github.com/zibo-chen/codex-defer-and-resume#readme) [stop_hook.py](https://github.com/zibo-chen/codex-defer-and-resume/blob/main/skills/defer-and-resume/scripts/stop_hook.py) [defer.py](https://github.com/zibo-chen/codex-defer-and-resume/blob/main/skills/defer-and-resume/scripts/defer.py)

当前上游实现的重要细节包括：

- 本地 filesystem polling 默认每 0.5 秒一次，这不调用模型。
- Stop hook 默认每 1,500 秒产生一次 cache-keepalive continuation；README 明确说这基于经验 cache horizon，不是 OpenAI 保证。因此它减少了模型 polling，但不是严格的零 model wake。
- 未确认 completion 默认 60 秒后重发 wake；日志、metadata、worker、result、wake、ack 分文件保存。
- worker 支持 timeout、cancel 和 stale-worker result，并把完整输出外置。
- App 和 task 必须在等待期间保持打开，且要求承载面支持 Stop Hooks。

它的优点是数据面清楚、日志不灌入 conversation、正常 filesystem polling 几乎无 token 成本。主要局限是：

1. 最后一跳仍依赖 Codex `Stop decision:block`，正好落在上节所列 Desktop/CLI 故障面上。
2. 它检测的是 process/result 状态，不理解“进程仍活着但训练已失去有效进展”的语义；要解决 silent stall，仍需 task-specific heartbeat/watchdog。
3. keepalive 会人为创建 model continuation，并可能重新引入 token、上下文和 UI 噪声。
4. process completion 只证明命令结束，不证明部署、数据迁移或科研 claim 已成功；README 也明确提示这一点。

因此它展示了正确的 supervisor/evidence-plane 方向，但在 Codex Desktop 当前条件下，不宜直接恢复成“唯一自动监督链”。

## 4. 成熟 supervisor 与调度器已经验证的模式

### 4.1 systemd：本机进程、watchdog、失败路由和日志分离

systemd service 可以按非零退出、signal、operation timeout 或 watchdog timeout 区分 failure；`WatchdogSec=` 要求服务定期发 `WATCHDOG=1`，超时会进入 failed；`Restart=` 可以对失败或 watchdog 自动重启，`RestartSteps=`/`RestartMaxDelaySec=` 支持逐步扩大重启间隔。[systemd.service upstream manual source](https://github.com/systemd/systemd/blob/main/man/systemd.service.xml)

`OnFailure=` 可以在 unit failed 时激活专门的 notifier/collector unit。[systemd.unit upstream manual source](https://github.com/systemd/systemd/blob/main/man/systemd.unit.xml) stdout/stderr 可进入 journal，`journalctl` 能按 unit 过滤，journald 支持持久/易失存储、容量限制与 rate limiting。[journalctl](https://www.freedesktop.org/software/systemd/man/255/journalctl.html) [journald.conf](https://www.freedesktop.org/software/systemd/man/252/journald.conf.html)

这说明本机长任务不需要 agent 保持 process ownership。限制在于 heartbeat 必须由应用或 wrapper 提供；“日志静默”不总是故障。自动 restart 也只有在任务幂等或可从 checkpoint 恢复时才安全。

### 4.2 Slurm：训练/批任务的事件通知、依赖与 checkpoint 预警

Slurm `sbatch` 提交后立即返回 job ID，stdout/stderr 默认写 `slurm-%j.out`，而不是留在提交终端。[Slurm sbatch](https://slurm.schedmd.com/sbatch.html)

它提供成熟的状态事件：

- `--mail-type=END,FAIL,REQUEUE,TIME_LIMIT...` 基于 job 状态通知；默认不发邮件。
- `--dependency=afterok:...`、`afternotok:...`、`afterany:...` 让后续 job 在成功、失败或任意终止后触发，无需人或模型轮询。
- `--time` 到期会 SIGTERM，随后 SIGKILL；`--signal` 可以在 time limit 前预警，让任务保存 checkpoint。
- `squeue --iterate` 可以轮询，但官方也提供 `--only-job-state` 降低 controller 查询负担，说明即使非模型系统也要控制监控成本。

来源：[Slurm sbatch](https://slurm.schedmd.com/sbatch.html) [Slurm squeue](https://slurm.schedmd.com/squeue.html)

Slurm 能理解 job/resource/node 状态，却不理解科研指标是否有效。requeue 从 batch script 开头重跑，所以同样依赖 idempotency 和应用 checkpoint。

### 4.3 GitHub Actions：完成 webhook、失败通知与 artifact

GitHub Actions 支持 workflow 完成通知，并可只订阅 failure；`workflow_run` 和 `workflow_job` webhook 有 `completed` event，可由外部服务事件订阅而非轮询。[Workflow notifications](https://docs.github.com/en/actions/concepts/workflows-and-actions/notifications-for-workflow-runs) [Webhook events](https://docs.github.com/en/webhooks/webhook-events-and-payloads)

`needs` 构成依赖图，上游失败时下游默认跳过，`if: always()` 可运行统一 collector/notifier；job/step 支持 timeout。完整 log、core dump、测试结果和截图可以作为 artifact 保存，只把 run URL、结论和少量摘要交给 agent。[Using jobs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs) [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) [Workflow logs](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs) [Workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts)

它适合 CI 和远程 workflow，本机 GPU/训练通常需要 self-hosted runner 或 Slurm。timeout/exit code 仍不等于语义健康，retry 也不应默认无条件执行。

### 4.4 tmux：可断开终端，但不是 supervisor

tmux session 可在 SSH 断开或 detach 后继续并重新 attach；`pane-exited` hook 和 `pipe-pane` 可用于退出通知与日志外置。[tmux Getting Started](https://github.com/tmux/tmux/wiki/Getting-Started) [tmux canonical manual](https://man.openbsd.org/tmux.1)

但 tmux 不负责 host reboot、server crash、timeout、health watchdog、依赖图或安全重试。它是 transport/UI containment，不应单独作为监督层。

## 5. 推荐的三层混合监督架构

以下是基于上述一手资料的架构推断，不是任何单一产品的官方保证。

三层职责应明确分开：第一层是零 token 的执行/监督层，持有进程、scheduler state、timeout 和 watchdog；第二层是外置证据与通知层，保存日志/checkpoint，并只在状态跃迁时投递有界事件；第三层是 agent 决策层，被唤醒后才做语义诊断与后续动作。第二层同时通知人，是当前 Codex 自动 re-wake 失效时的可靠降级路径。

```text
agent 只负责定义任务合同并启动
                │
                ▼
runner / scheduler 持有进程 ──────► 完整日志、checkpoint、artifact
                │
                ├─ exit / timeout / known fatal pattern
                ├─ sustained heartbeat or progress stall
                └─ explicit needs-input marker
                │
                ▼
        bounded attention event
        task_id, state, exit_code,
        last_progress_at, evidence paths,
        short deduplicated diagnostic tail
                │
          ┌─────┴────────┐
          ▼              ▼
   reliable human     best-effort agent wake
   notification       after version smoke test
          └─────┬────────┘
                ▼
      agent reads result first, expands evidence only if needed
```

### 5.1 状态与证据平面

每个 job 至少应外置：

- `metadata`: task id、command identity、cwd、start time、timeout、owner；
- `state`: `starting | running | completed | failed | timed_out | stalled | cancelled`；
- `progress`: application heartbeat、latest step/epoch、last artifact timestamp、关键业务 metric；
- `result`: exit code、end time、failure class、checkpoint/artifact 路径；
- `output`: 完整 stdout/stderr 或调度器 log；
- `attention`: 单调递增 event id、首次触发时间、是否已确认。

写入应原子化，notification 至少一次投递，consumer 按 event id 去重。对话中只传 `attention` envelope，不传完整日志。

### 5.2 异常 watchdog：检测而不擅自处置

廉价 watcher 可以监控：

- process/job state 是否进入终态；
- application heartbeat 是否超过阈值；
- checkpoint、metrics 或 artifact mtime 是否持续不变；
- GPU/CPU 利用率是否在一个持续窗口低于任务特定阈值；
- 已知且高精度的 fatal log pattern；
- deadline、disk space 或 scheduler time limit 预警。

单一瞬时信号不应立即判死；应用 heartbeat 通常比“日志有没有新行”可靠。watchdog 只授予“检查证据”的机会，不自动授权 cancel、restart、改超参或启动下一阶段。

### 5.3 事件优先；不能订阅时再做分层、自适应轮询

优先使用 `waitpid`/process exit、systemd unit transition、Slurm dependency/mail、GitHub webhook 等事件。若目标系统只有 status API，则轮询放在宿主脚本而不是模型中：

- 高频检查便宜字段：PID/job state、heartbeat timestamp、mtime；
- 低频检查昂贵字段：远程 API、GPU telemetry、语义日志分析；
- 健康稳定时指数退避并加入 jitter；接近 deadline 或出现异常趋势时临时提高频率；
- 只在状态改变或持续越界时输出一次事件，正常采样写外部状态而不进入 conversation。

这里“自适应轮询”减少的是系统查询与噪声；真正消除 token 消耗的关键仍是轮询程序不调用模型。

### 5.4 通知分级

- `completed/success`：短通知；如果没有后续自动阶段，可以只提醒人，不必唤醒 agent。
- `failed/timed_out/stalled/needs_input`：立即 attention event，并附最小诊断摘要。
- transient infrastructure error：只有在错误分类明确、retry 有上限且任务幂等时才由 supervisor 自动 retry。
- code bug、OOM、permission、数据质量异常：唤醒 agent/人判断，不盲目 retry。

### 5.5 checkpoint 与上下文卫生

runner 保存全量日志；应用保存真正可恢复的 checkpoint；supervisor 保存 latest state snapshot 和少量状态跃迁记录。agent resume 时按顺序读取：

1. `result/attention`；
2. 相关 checkpoint/metric summary；
3. 日志最后几十行或错误附近窗口；
4. 只有仍无法判断时才扩大日志范围。

这样即使任务运行数天，对话也只增加一次短结果，而不是数百条“仍在运行”。

## 6. 对当前环境的建议路线

### 近期可靠基线

1. 本机普通长命令交给 user-level systemd service/transient unit 或项目已有 runner；集群训练交给 Slurm；CI 留在 GitHub Actions。
2. 让任务自己写 heartbeat/progress/checkpoint，完整日志留在 journal、Slurm output 或 job artifact。
3. 用 supervisor 的终态/timeout/watchdog 产生一次本机系统通知或其他用户可见通知。
4. 用户回到同一 Codex task 后，提供 task id 或 result path；agent 只消费结构化结果和必要日志。
5. `/goal` 留给被唤醒后的诊断、修复、重试验证或多阶段推进，不用于“下一小时只能等”的区间。

这条路线已经解决 token 和上下文污染，同时把故障发现延迟从“人偶然想起来”缩短到宿主 watcher 的检测窗口；唯一没有自动化的是最后的 agent re-entry。

### 自动 agent re-entry 的启用门槛

如果未来 Codex 提供类似 Claude `asyncRewake` 的原生事件，或者 Desktop `Stop` continuation 在目标版本稳定，可以把同一个 attention event 同时送到 agent。但应满足：

- fresh root task 和 delegated/subagent task 都通过固定 sentinel；
- success、non-zero exit、timeout、interrupt、rate-limit 和 App restart 分别验证；
- 每个 completion 只产生一个可去重 wake；
- delivery failure 有人类通知 fallback；
- watcher 不向对话发送 heartbeat；
- 版本升级后重新 smoke test，而不是把一次通过当成平台永久保证。

在这些条件满足前，不建议重新用长时间 `Stop` hook 持有等待，也不建议用 keepalive continuation 模拟 durable event bus。

## 7. 方案选择表

| 场景 | 推荐 | 不推荐作为主要机制 |
| --- | --- | --- |
| 多步迁移、修复、实验迭代，每轮都能推进 | `/goal` + 明确 checkpoint/停止条件 | 无目标的固定频率 status prompt |
| 单个本机训练/构建，长时间无可操作动作 | systemd/项目 runner + heartbeat + system notification | 让 agent 每几分钟查 PID/日志 |
| HPC/GPU 集群任务 | Slurm state/mail/dependency/signal + application checkpoint | 在 Codex turn 中循环 `squeue` |
| CI/部署 workflow | GitHub Actions webhook/notification + artifacts | agent 轮询 REST API |
| 仅需 SSH 断开后继续 | tmux 可作 transport；另加 supervisor/watchdog | 把 tmux 本身视为健康监控和重试系统 |
| 要求异常时自动让 agent 介入 | 事件 watcher + 经版本验证的 re-wake + 人类 fallback | 只依赖 Codex Desktop `Stop decision:block` |

## 最终判断

社区已有一个相当一致的答案：**不要让模型负责“等待时间的流逝”，让模型负责“事件发生后的判断”**。系统级 supervisor 解决进程存活、终态、timeout、日志和 heartbeat；agent 只在真正有新信息时恢复。Claude Code 的 Monitor/`asyncRewake` 已经把这个模式产品化；Codex Hooks 具备外置证据和 continuation 组件，但 Desktop 的最后一跳目前仍需版本级验收与人类通知 fallback。

因此，最佳折中不是在轮询频率上做小修，而是改变监督边界：把高频但廉价的检查留在宿主，把低频但昂贵的语义判断留给 agent，把完整证据留在文件/调度器，把 conversation 限制为状态跃迁摘要。
