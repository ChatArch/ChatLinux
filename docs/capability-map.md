# 能力地图

这个页面用于校对 `ChatLinux` 当前有哪些一等能力、哪些能力已经验证，以及哪些事情不属于当前包。

## 能力分组

<div class="grid cards" markdown>

- **Fleet 状态缓存**

    通过配置文件 track 一组 Linux 服务器，用 Ansible 刷新常规指标，并把配置、cache、runtime inventory/probe 都放在 ChatArch home 内部。

- **命令行入口**

    `chatlinux fleet init/refresh/show/status` 提供 shell-friendly 操作；`show` 默认只读本地缓存。

- **Python 接口**

    实质能力在 `chatlinux.fleet` 中实现，Click 命令只负责参数解析和输出。

- **配置与环境**

    默认状态根为 `CHATLINUX_HOME` > `$CHATARCH_HOME/chatlinux` > `~/.chatarch/chatlinux/`，包含 `fleet.json`、`cache/` 和 `runtime/`；`init --json` 会输出完整 `state_paths`。

</div>

## 当前边界

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| 命令行基础入口 | 已实现 | Click group、`--version` 和基础测试。 |
| ChatEnv 配置提供者 | 已实现 | `config.py` 和 `chatenv.configs` 入口点保留，用于 ChatEnv 发现。 |
| Fleet sample 配置 | 已实现 | `chatlinux fleet init --sample cube` 写入 `.cube` track。 |
| Fleet refresh | 已实现 | `chatlinux fleet refresh --track cube` 生成 Ansible inventory/probe，运行只读采样并写缓存。 |
| Fleet cache 查看 | 已实现 | `show` / `status` 从 `cache/<track>-status.json` 读取，不访问服务器。 |
| JSON 输出 | 已实现 | `init`、`refresh`、`show`、`status` 均支持 `--json`。 |

## 当前采集指标

- hostname、采样时间、uptime、CPU count、load average；
- memory total/available、swap total/used；
- 文件系统容量；
- `nvidia-smi` 可用时的 GPU 信息；
- `systemctl --failed` 失败 unit 名称。

## 不在当前范围

- 不执行 sudo。
- 不清理、不重启、不修复远端服务。
- 不采集需要特权的 SMART/NVMe 寿命数据。
- 不把未实现能力写成用户可执行教程。
- 不在 README、docs、issue、PR 评论或 CI log 中输出 secret、token、cookie 或 Authorization header。
