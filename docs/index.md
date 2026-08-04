# ChatLinux 文档

ChatLinux 是 ChatArch 系列 Linux 运维包。当前首个业务能力是 **fleet 状态缓存 CLI**：用 ChatArch 内部配置 track 服务器，通过 Ansible 刷新常规公共指标，并从本地缓存快速查看状态。

站点入口：<https://arch.gh.wzhecnu.cn/ChatLinux/>

## 按场景选择文档

| 场景 | 文档 |
| --- | --- |
| 第一次安装、初始化 `.cube` track、刷新/查看缓存 | [快速开始](quickstart.md) |
| 查看当前真实 CLI 命令树和 shell 用法 | [CLI 树](cli-tree.md) |
| 校对当前包有哪些一等能力和边界 | [能力地图](capability-map.md) |
| 从 Python 代码调用包能力 | [Python 接口树](interface-tree.md) |

## 核心入口

<div class="grid cards" markdown>

- **快速开始**

    初始化 `fleet.json`，刷新 `.cube` 状态，并通过缓存快速查看。

    [查看快速开始](quickstart.md)

- **CLI 树**

    从命令行入口开始，记录已实现命令、命令状态和交互约定。

    [查看 CLI 树](cli-tree.md)

- **能力地图**

    用于 review 当前包的能力边界，避免把规划写成已实现功能。

    [查看能力地图](capability-map.md)

- **Python 接口树**

    保持命令行是薄入口，实质能力放在可 import 的 Python 接口中。

    [查看接口树](interface-tree.md)

</div>

## 当前默认路径

默认本地状态根：`CHATLINUX_HOME` > `$CHATARCH_HOME/chatlinux` > `~/.chatarch/chatlinux`。默认落点：

```text
~/.chatarch/chatlinux/fleet.json
~/.chatarch/chatlinux/cache/<track>-status.json
~/.chatarch/chatlinux/runtime/fleet-inventory.ini
~/.chatarch/chatlinux/runtime/fleet_probe.py
```

`show` / `status` 默认只读缓存；`refresh` 和 `status --refresh` 才会访问服务器。`init --json` 会输出完整 `state_paths`，用于确认 config/cache/runtime 都仍在 ChatArch 内部路径。

## 本地预览

```bash
python -m pip install -e ".[docs]"
mkdocs serve
```

英文首页见站点语言入口：<https://arch.gh.wzhecnu.cn/ChatLinux/en/>。
