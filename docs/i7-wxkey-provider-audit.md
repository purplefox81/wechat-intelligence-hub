# i7 wxkey provider 审核

2026-09-12 在 i7 上完成源码、构建和 Reader 接入计划审核。本文记录的是待授权候选，**没有执行 provider，也没有取得或读取任何访问材料**。

## 结论

当前唯一建议进入一次有界实机尝试的候选是 [`r266-tech/wxkey`](https://github.com/r266-tech/wxkey) 提交 `01e96fa58ce3ff061dce83e4c36f62104ebc6b16`。此前审核的 `9b70eec` 基线缺少 Intel PBKDF 参数解码；上游后续两个提交只加入 `x86_64` 参数映射及测试，并保留原有 ARM 路径。i7 必须使用新提交，不能复用 M3 的 ARM 二进制或旧哈希。

其他仓库没有提供更小、更确定的 i7 获取路线：

| 仓库/路线 | 审核提交 | 结论 |
|---|---|---|
| `Rion-Wu-tech/wechat-intelligence-hub` / 本项目 Reader | `6cc1f8118a480c1eb07598c806cae711b8bccd51` | 业务分析与只读读取层；不自带独立获取实现，仍由经审核的 provider 提供首次访问材料。 |
| `ops120/wechat-local-viewer` | `fe6a76d75273456a5073afe2883ef8fbb4e41ee3` | 只消费 `decrypted/` 或 `.decrypted/` 明文目录，不能解决首次访问。 |
| `JackyCufe/signal-vaults` | `a5a58b0e2a3779f820d0c612a362578c50a06d27` | 业务层依赖未固定 `main` 的 `maomao3334/wechat-cli-plus`，本身没有独立获取实现。 |
| `maomao3334/wechat-cli-plus` | `75a322dd09c7c498536d10ff6935c5d52fd5fd2b` | i7 所需 `find_all_keys_macos.x86_64` 未随仓库提供；失败后会直接重签 `/Applications/WeChat.app`，并扫描所有账号目录，因此不采用。 |
| `mcncarl/yichen-skills/yichen-wechat-local-vault` | `fc575e5112eb4d4d5ea155f1f0cfd79621834006` | 使用 Frida 注入重签名副本并把 PBKDF 输入和派生结果写到 `/tmp/wechat_frida_keys.log`；依赖和敏感落盘面更大，因此不采用。 |

## i7 固定构建

- 主机：`ycm-mac-air-i7.local`，`x86_64`
- 微信：`4.1.13`
- Go：Homebrew `go1.27.1 darwin/amd64`
- 源码：`~/Library/Application Support/rion-wechat-reader-i7/providers/wxkey-01e96fa/source/`
- 二进制：`~/Library/Application Support/rion-wechat-reader-i7/providers/wxkey-01e96fa/bin/wxkey`
- 提交：`01e96fa58ce3ff061dce83e4c36f62104ebc6b16`
- SHA-256：`ef917e01b316e02a8ecb3556429c406ffeac39c8ab4cdaf506a6bd11d7771541`
- 文件：`Mach-O 64-bit executable x86_64`
- 权限：`0700`，属主为当前桌面用户

`go test ./...` 全部通过。构建信息包含上述源码提交、`vcs.modified=false`、`GOARCH=amd64` 和唯一外部依赖 `github.com/ebitengine/purego v0.10.0`。构建时下载了 Go 模块；审核未在 provider 运行代码中发现网络调用。

## 源码与副作用

Reader 的授权 worker 以 root 调用固定二进制，并只传入筛选后的环境：`WXKEY_NO_ELEVATE=1`、`WXKEY_ELEVATED=1`、当前用户的 HOME/USER 和超时参数。`wxkey` 的 `ensureStoredSudoPassword` 在 root 下立即返回，因此这条调用路径不会读取、索取或保存管理员密码；密码只由 macOS 系统授权窗口处理。这是对上述精确源码和构建的结论，不适用于其他二进制。

没有设置 `WXKEY_BOOTSTRAP_ORIGINAL_WECHAT`，所以官方 Hardened Runtime 微信会进入 shadow 路线。一次实际运行会：

1. 请求 macOS 管理员授权并取得进程调试访问。
2. 退出当前微信，复制官方应用到 `~/Library/Application Support/wx-mcp/WeChat-shadow.app`，只对该副本做 ad-hoc 签名。
3. 启动 shadow 微信，扫描其进程内存；被动扫描不足时，可能启动 LLDB PBKDF 断点回退。
4. 把匹配到的材料以 `0600` 写入 `~/.config/wxcli/config.json`，随后由 Reader 私下验证并发布自己的配置；provider 标准输出和错误输出被抑制。
5. 正常清理时停止 shadow 微信，并在原微信此前运行的情况下重新打开官方应用。

这条路线不会主动重签 `/Applications/WeChat.app`。不过，退出微信、运行重签名副本和访问进程都是真实副作用；微信 4.1.13 与 i7 的端到端兼容性、图形界面超时后的完全清理以及账号零风险均无法由静态审核保证。

## Reader 计划验收

对当前账号的 19 个数据库执行 `rion-wechat-access plan` 和不带 `--apply` 的 `onboard`：

- provider SHA-256 精确匹配；
- `provider_executed=false`；
- `key_acquisition=false`、`configuration_write=false`；
- 状态为 `authorization_required`；
- 19 个数据库仍全部 unresolved。

验收前后均确认不存在 `wxkey`/shadow/Reader 获取进程，不存在 `~/.config/wxcli/config.json`、shadow 应用和 `recovery-required.lock`。原 `/Applications/WeChat.app` 仍为 Tencent Developer ID 签名，Team ID 为 `5A4RE8SF68`。

## 有界尝试与恢复

获准后只运行一次 Reader `onboard --apply`，锁定本文的绝对路径和 SHA-256，不直接调用 provider，也不改用其他候选。用户只在 i7 的 macOS 系统授权窗口输入密码。

成功标准是 Reader 返回 `state=ready`、`live_database_read_ok=true`，然后能从数据库读取并抽检已知最近私聊；只获得部分 key、进程退出码为 0 或通知预览可读都不算成功。

失败、取消或超时后停止重复尝试。先检查 `~/.config/rion-wechat-reader/access-runs/` 的固定结果和恢复锁、运行中的 provider/shadow 进程以及官方微信签名；保留已经生成的材料用于单独验证，不在终端或对话中输出。确认 shadow 已退出、官方微信能正常启动并且失败原因明确后，才考虑是否另行授权重试。

## 2026-09-12 首次执行结果

用户已明确授权一次 `onboard --apply`。第一次从 SSH 会话启动时，macOS `authd` 报告 `session has no ui access`，provider 未启动；随后改从 i7 当前 Aqua 图形会话启动同一固定命令，但 TCC 的 App Data 权限请求一直未完成，进程停在读取数据库根目录的检查点。已终止该实例并卸载临时 LaunchAgent。

最终状态：`provider_executed=false`、`key_acquisition=false`、`configuration_write=false`；无 shadow 应用、无 `wxcli/config.json`、无 provider 进程，官方微信仍在运行且保持腾讯 Developer ID 签名。Reader 私有结果标记为 `authorization_ui_not_confirmed`。若再次尝试，需先在 i7 本机的“系统设置 → 隐私与安全性”中为实际运行的终端/Python 授予访问微信容器所需的“文件与文件夹”或“完整磁盘访问”权限，再重新走一次同样的恢复审查。

随后用户批准了 TCC 和管理员授权，重试一次固定候选。该次进入了 shadow 准备流程，但 worker 返回 `provider_failed`，没有写出访问材料；官方微信随后已重新打开。shadow 曾因 root 所有的父目录无法由普通用户直接移动，最终经用户批准的管理员清理任务移入 `~/.Trash/WeChat-shadow.app`。清理后确认无 shadow/provider 进程、无 `wxcli/config.json`，官方微信仍为腾讯 Developer ID 签名，恢复锁继续保留。失败原因未从被抑制的 provider 输出中臆测，不再自动重试。

用户随后再次明确要求重试，并再次完成 TCC/管理员授权。第三次执行仍返回 `provider_failed`：provider 启动并创建 shadow 后未生成访问材料，官方微信已恢复运行。shadow 已经用户批准移入 `~/.Trash/WeChat-shadow-retry-20260912.app`；临时清理任务已卸载。最终确认无 provider/shadow 进程、无 `wxcli/config.json`，官方微信保持腾讯 Developer ID 签名，恢复锁仍保留。连续两次在授权成功后失败，说明问题不在密码输入时机；本路线停止，不再盲目重试。

## 2026-09-12 wechat-cli-plus C 扫描尝试

按用户选择准备并运行一次 Intel C 扫描器：源码固定为 `maomao3334/wechat-cli-plus` 提交 `75a322dd09c7c498536d10ff6935c5d52fd5fd2b`，i7 原生构建二进制 SHA-256 为 `8c49e1e6dfcaaa802e51f50d3627dbc832c1241da39e8d017928a824b09fa190`。本次只调用 C 二进制，不调用 Python 包装层，因此不会自动重签 `/Applications/WeChat.app`。

管理员授权后扫描器退出码为 `1`，没有生成 `all_keys.json`；为避免在终端或对话中暴露 key，标准输出和错误输出均丢弃。执行期间微信未退出，之后确认无扫描器/provider/shadow 进程，原微信仍为腾讯 Developer ID 签名。该路线未取得访问材料；由于没有保留原始输出，不能从本次结果推断具体失败原因，也不再自动切换到直接重签原版微信。

## 2026-09-12 yichen Frida 高侵入尝试

用户明确授权对 i7 上的微信副本进行 Frida 注入，并在本机生成原始 key 日志和明文 vault。源码固定为 `mcncarl/yichen-skills` 提交 `fc575e5112eb4d4d5ea155f1f0cfd79621834006`，放在 i7 的隔离 provider 目录；依赖固定为 Frida `17.18.0`、frida-tools `14.10.4`、PyCryptodome `3.23.0`、zstandard `0.25.0`。

实机结果分三层记录：

1. 上游脚本的 `CCKeyDerivationPBKDF` Hook 成功安装，但 120 秒内捕获 `0` 次调用；登录副本并打开目标聊天后仍为 `0`。
2. 额外 Hook `libsqlite3.dylib` 的 `sqlite3_key` 与 `sqlite3_key_v2`，两个入口均安装成功，重启已登录副本后仍为 `0` 次。
3. 额外 Hook CommonCrypto `CCCrypt*`、OpenSSL `EVP_*Init_ex` 和 AES 256-bit 候选入口，11 个入口安装成功，但唯一 32 字节候选为 `0`，数据库匹配为 `0`。

第二层确认副本实际打开了该账号 `db_storage` 下的 69 个数据库相关文件；因此失败不是未登录或未打开数据库。当前微信 4.1.13 使用了未被这些公开入口覆盖的 WCDB/内部加密路径，yichen 方案在此版本上没有取得 key，未生成明文 vault。

恢复验收：停止所有副本和 Frida helper；删除空的 `wechat-keys.json`、配置文件和 `/tmp/wechat_frida_keys.log`；将约 1.4GB 的 ad-hoc 副本移入 i7 `~/.Trash/WeChat-frida-20260912.app`；重新启动 `/Applications/WeChat.app`。官方微信 PID `86602` 正常运行，Tencent Developer ID 签名与 `codesign --verify --deep --strict` 均通过。该路线不再继续盲目重试。
