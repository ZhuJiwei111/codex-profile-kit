# Remote Task Bridge（可选组件）

此目录维护 Windows 隔离 Desktop 适配器与 Linux stdio helper 的源码。它不属于便携 profile，不注册为默认安装插件，不由 `profile_sync.py` 或 `plugin_sync.py` 部署或启用。同步 Git 源码不等于启用远端能力。

状态：原实验已真实验证直接目录创建、默认 worktree、不同父任务、原生审批批准/拒绝、显式停止及回滚恢复。本目录为参数化后的维护版本；本地检查不能替代它在每个新主机上的集成验收。适配器仅针对 Desktop 包 26.901.4073.0 的已检查内部入口；其他版本若入口不匹配会拒绝构建。

## 授权与状态

复制 `config.example.json` 到仓库外的主机本地目录，填写官方程序目录 `sourceApp`、全新的隔离目录 `stateRoot`、SSH alias、可执行路径及允许的项目。模板默认 `enabled: false`，明确审阅后改为 true。一个配置绑定一个 SSH 主机；本版不提供全主机 fan-out，不应在多个运行实例间复用远端 socket 目录。

`stateRoot` 保存独立程序副本、用户资料、请求记录、日志和回滚备份，须在本地磁盘，不能放进仓库或云同步目录。远端 `remoteDirectory` 为当前用户专用目录；不要使用共享目录。不得复制官方登录资料、session、trust 或凭据来准备新实例。首次登录由用户在隔离窗口完成。

运行需要 Windows 桌面常驻与 SSH 通道；这不是服务器脱离桌面独立创建任务的服务。构建会更新 ASAR 格式要求的完整性字段，但测试程序的厂商签名不再有效。正式安装始终只读。源码本身不包含程序包或认证状态。

## 独立命令

Windows 使用 PowerShell 7；Python 使用本机 `HOST_LOCAL.md` 指定的解释器（Python 3.11+），Node 使用已安装运行时。以下 `$config` 指向仓库外的配置文件。

```powershell
$config = 'C:\host-local\remote-bridge.json'
./prepare.ps1 -Config $config
# 会复制一份程序，需先确认本地空间充足；不会复制已有用户资料。
& $env:PROFILE_PYTHON ./build.py --config $config
./switch.ps1 -Config $config
```

`prepare` 只接受不存在的新状态目录，避免覆盖旧实例。准备失败时保留现场，不自动删除目录。`build` 仅从指定原件生成暂存补丁；`switch` 才停止自己的实例、保留首次安装前程序备份、安装暂存版本并启动。

```powershell
./switch.ps1 -Config $config -StopOnly
./start.ps1 -Config $config
./switch.ps1 -Config $config -Rollback
```

`StopOnly` 是确定性停止入口，核对路径后停止隔离程序与已记录的 SSH。菜单关闭可能仅隐藏窗口，自动退出回收尚未证明。`start` 补齐远端 helper，并仅清理当前用户拥有、无监听且检查期间未变化的精确 socket；不覆盖活跃通道。`Rollback` 恢复首次安装前的程序，保留独立用户资料与请求记录；恢复新版则重新执行 `switch`。未修改配置时无需重新构建；授权项目或连接配置变更后必须重新构建。

## 工具合同

`remote_tasks.create_thread` 接受必填 prompt、可选 title 和 environment（local/worktree）。只在用户明确要求新建任务时使用。Git 项目默认 worktree，非 Git 默认 local；直接使用原目录必须明确选择 local。目标由 Desktop 项目映射及配置白名单确定，不接受任意来源 ID、主机、目录或权限覆盖参数。

保持原生 prompt 审批；approval_policy=never 不会被自动放宽。来源必须为当前运行回合。可信边界是同一 Windows 用户与同一远端 Unix 用户；本组件不声称隔离同账号恶意进程。执行器的稳定调用 ID 用于持久去重，同一已完成请求返回保存结果；派发后断线结果未知时不自动重试。新调用 ID 是新请求，不承诺跨新调用自动去重。clientThreadId 表示排队，不能冒充正式 threadId。

## 检查与推广

```powershell
node ./core.test.cjs
& $env:PROFILE_PYTHON ./mcp_test.py
& $env:PROFILE_PYTHON ./configuration_test.py
```

构建检查需使用真实官方包和仓库外配置。新主机先单独启用一个项目，验收原生拒绝不派发、批准后父子关系与目录、默认 worktree、停止回收及重启通道，再扩大项目范围。非 Git 和重放分支以本地测试为基础；从 worktree 父任务继续创建尚需真实验证。

普通 profile 同步行为不变。后续如需将本组件改为插件、加入默认同步或部署到新主机，应单独审阅该边界变更；不能仅向现有插件同步器追加硬编码名称。
