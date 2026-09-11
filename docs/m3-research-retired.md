# M3 微信读取研究已停止

2026-09-11，用户决定停止在 M3 上研究微信读取及自动化。此记录不是重启研究的授权。

## 清理结果

- 项目外的 `wechat-wxkey-audit`、provider 二进制、Reader 失败记录与恢复锁、重签名微信副本、Go 模块及构建缓存、Go 遥测目录，均已移至本项目 `.local-archive/m3-wechat-retired/`。
- 本次新增的 Homebrew Go 1.27.1、SQLCipher 4.19.0、OpenSSL 4.0.2 已卸载；对应下载缓存与遗留 OpenSSL 配置已归档。
- `.local-archive/` 被 Git 忽略，不提交、不推送；迁入的虚拟环境和二进制仅作历史留存，不作为可运行环境维护。
- 原始 `/Applications/WeChat.app` 保留，清理后代码签名校验通过；微信账号目录、聊天数据库和用户设置未修改。
- 清理时未发现运行中的 wxkey、Reader 或 shadow 微信，也未在用户 LaunchAgents、Codex automations 和 shell 启动文件中发现本研究的启动引用。
- 系统 Python 中未检测到 sqlcipher3、pysqlcipher3、zstandard；成功安装的驱动仅在已归档虚拟环境中。

## 研究结论的限制

两次 provider 尝试均失败，未验收实时聊天读取。此前仅凭目录大小、更新时间和通用失败码推断账号归属或失败阶段，证据不足，不能作为已确认事实。原有失败记录保留在忽略归档内，不再重试。
