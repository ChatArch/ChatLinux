# CLI 树

这篇文档展示 `ChatLinux` 当前已实现的命令树。命令背后的可 import Python 函数见 [Python 接口树](interface-tree.md)，能力边界见 [能力地图](capability-map.md)。

`chatlinux --tree` 由 ChatStyle 从 Click 注册表生成真实命令树，默认包含参数签名；release 验收以这个输出为准：

```text
chatlinux
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
└── fleet [--home HOME]  # Track server fleets and view cached health status.
    ├── init [--sample SAMPLE] [--force] [--json]  # Initialize a fleet config under the ChatLinux state directory.
    ├── refresh [--track TRACK] [--json]  # Run Ansible read-only checks and update the local cache.
    ├── show [--track TRACK] [--json]  # Show the last cached fleet status without contacting hosts.
    └── status [--track TRACK] [--refresh] [--json]  # Show cached fleet status, optionally refreshing first.
```

`chatlinux --tree-brief` 省略参数签名，但保留命令节点与说明：

```text
chatlinux
├── --help  # Show this message and exit.
├── --version  # Show the version and exit.
├── --tree  # Print the registered CLI tree and exit.
├── --tree-brief  # Print the registered CLI tree without parameter signatures and exit.
└── fleet  # Track server fleets and view cached health status.
    ├── init  # Initialize a fleet config under the ChatLinux state directory.
    ├── refresh  # Run Ansible read-only checks and update the local cache.
    ├── show  # Show the last cached fleet status without contacting hosts.
    └── status  # Show cached fleet status, optionally refreshing first.
```

## 常用 shell 流程

```bash
chatlinux fleet init --sample cube
chatlinux fleet refresh --track cube
chatlinux fleet show --track cube
```

任务目录隔离状态：

```bash
chatlinux fleet --home ./playground/chatlinux-home init --sample cube --json
chatlinux fleet --home ./playground/chatlinux-home status --track cube --refresh
```

## 状态约定

| 状态 | 含义 |
| --- | --- |
| 已实现 | 命令、函数和测试已经存在 |
| 已验证 | 已通过本地测试、shell smoke 或真实 Ansible refresh |
| 规划 / checkpoint | 只保留边界说明；实现前不要写操作教程 |

## 更新清单

- 新增命令时，同步更新 CLI 树、能力地图、接口树、README、测试和 changelog。
- 会访问远端的命令必须说明是否只读、是否使用 sudo、是否写缓存或远端状态。
- `show` / `status` 默认只读本地缓存；`refresh` 和 `status --refresh` 才会访问服务器。
