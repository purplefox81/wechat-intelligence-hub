# i7 微信读取准备记录

2026-09-11 通过 M3 的 SSH 别名 `i7` 完成只读检查。后续微信读取和自动化实验转移到 i7；M3 不再运行微信读取研究。

## 已确认

- 主机：`ycm-mac-air-i7.local`
- 系统：macOS 15.7.9，`x86_64`
- 微信：`/Applications/WeChat.app`，版本 `4.1.13`
- 微信容器：`~/Library/Containers/com.tencent.xinWeChat/`
- 数据根：`~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/`
- 当前运行进程实际打开的账号目录：`wxid_br72slr93x8112_574d`
- 当前账号数据库根：`~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_br72slr93x8112_574d/db_storage/`
- 当前账号目录约 15 MB；消息库 `message/message_0.db` 约 45 KB。

运行中的微信进程通过文件句柄打开了该账号的 `message_0.db`、`message_0.kvdb`、`message_fts.db`、`session.db`、`contact.db` 及对应 WAL/SHM 文件。这比按目录大小猜测账号归属更可靠。

## 当前状态

- Reader 已安装；本次未读取聊天内容、未获取密钥、未运行 provider、未修改微信或其数据库。
- Reader 代码和后续运行目录应放在 i7 独立工作区；不要把 i7 的微信数据复制回 M3。
- 后续如需运行 provider，必须在 i7 上重新审核适配 x86_64 与微信 4.1.13 的具体构建，并单独确认进程访问、重启和重签名副作用。

## i7 基础工具

2026-09-11 已通过 i7 的 Intel Homebrew/用户级 Python 安装并验证：

- `ripgrep` 15.2.0，命令 `rg`
- `fd` 10.5.0，命令 `fd`
- `ast-grep` 0.45.3，命令 `ast-grep`；通过官方 PyPI 包安装，并链接到 `~/.local/bin/ast-grep`

Homebrew 为 `ast-grep` 预编译依赖启动的 LLVM 编译已停止，残留的 `ninja` 已卸载；没有保留无关的编译进程。

i7 原本的 `~/.zshenv` 为空；已加入 `/usr/local/bin` 与 `~/.local/bin` 到 PATH，使普通 SSH 命令也能直接找到这三个工具。

## Reader 安装状态

2026-09-11 已将本项目的 `Rion WeChat Reader` 源码放入 i7 的独立目录：

- 源码：`~/Library/Application Support/rion-wechat-reader-i7/source/rion-wechat-reader/`
- 命令：`~/.local/bin/rion-wechat-cli`
- 运行环境：`~/.local/share/rion-wechat-cli/venv/`
- Reader：`0.9.2-preview.2`
- SQLCipher：`4.12.0 community`（隔离 venv）
- zstandard：`0.25.0`（隔离 venv）

`rion-wechat-cli self-test --require-sqlcipher` 已通过。对当前运行账号的 `db_storage` 目录执行只读 `access-plan`：扫描到 19 个数据库，但状态为 `needs_access`、`unresolved_databases=19`；没有写入 Reader 配置、没有获取密钥、没有运行 provider，也没有读取聊天正文。Reader 当前等待用户已有访问材料或另行审核的接入方案。
