# yichen-wechat-local-vault 代码审查

审查日期：2026-09-11

## 来源与 fork

`yichen-wechat-local-vault` 是 `mcncarl/yichen-skills` 仓库中的子目录，不是独立 GitHub 仓库。账号 `purplefox81` 已有父仓库 fork：
`https://github.com/purplefox81/yichen-skills`。该 fork 已与上游 `main` 同步，双方当前提交均为 `fc575e5112eb4d4d5ea155f1f0cfd79621834006`。

## 价值

- `vault_cli.py` 提供统一的联系人、会话、历史、搜索、统计、导出、收藏和朋友圈查询入口，命令形态和素材包设计可作为 Reader/Hub 的产品层参考。
- `snapshot_reader.py` 对离线快照做了路径组件检查、拒绝符号链接、SQLite `mode=ro&immutable=1`、`query_only`、WAL/SHM 拒绝、结果上限和不可信内容标记。这些边界对未来“只读离线快照”很有参考价值。
- Windows 快照模式与 Mac 活库路线分开，测试覆盖了快照输入不被修改和 SQLite 写操作被拒绝的情形。

## 与当前低侵入目标冲突的部分

- `scripts/extract_keys.py` 使用 Frida 注入 WeChat 进程，Hook `CCKeyDerivationPBKDF`，并把 `password`、salt 和派生 key 写入 `/tmp/wechat_frida_keys.log`；“日志中 redacted”的提示不改变其实际记录敏感材料的行为。
- 同一脚本会复制 `/Applications/WeChat.app` 到桌面并执行 `codesign --force --deep --sign -`，还支持附加到或启动重签名副本。这会触发进程访问、重签名和潜在重启副作用，不能作为当前 Reader 的默认路径。
- `decrypt_all_dbs.py` 会把加密库解密成包含明文聊天数据的本地 vault，并把 key 的哈希写入增量状态；它依赖外部 key 文件，且没有解决当前 i7 微信版本的访问材料问题。
- 仓库代码未发现向网络服务上传数据的实现；风险主要来自本地敏感材料落盘、进程注入、重签名和生成完整明文副本。

## 当前结论

只借鉴 `snapshot_reader.py` 的只读文件/SQLite 安全边界，以及 `vault_cli.py` 的查询接口设计；不运行、不安装 `extract_keys.py`，也不把该仓库的 Mac 密钥获取或重签名逻辑接入 i7 Reader。仓库自带测试在当前 M3 Python 环境因缺少 `zstandard` 依赖未能直接启动，不能据此宣称其测试全绿。
