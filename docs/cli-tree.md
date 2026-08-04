# CLI 树

这篇文档展示 `ChatLinux` 当前已实现的命令树。命令背后的可 import Python 函数见 [Python 接口树](interface-tree.md)，能力边界见 [能力地图](capability-map.md)。

## 顶层命令

```text
chatlinux                         # ChatLinux 命令行入口
├── --help                            # 显示 CLI 帮助和已注册命令
├── --version                         # 输出当前包版本
└── fleet                             # 管理/查看服务器 fleet 状态缓存
```

## Fleet 状态命令

```text
chatlinux fleet                   # 服务器 fleet 状态命令组
├── --home DIRECTORY                  # 覆盖 ChatLinux 状态目录；默认 ~/.chatarch/chatlinux
├── init                              # 初始化 fleet 配置、cache、runtime 目录
│   ├── --sample cube                 # 写入 ChatArch .cube sample track
│   ├── --force                       # 覆盖已有配置
│   └── --json                        # 输出机器可读 JSON，包含完整 state_paths
├── refresh                           # 通过 Ansible 只读刷新状态并写缓存
│   ├── --track cube                  # 选择要刷新的 track
│   └── --json                        # 输出完整缓存 JSON
├── show                              # 查看上一次缓存，不访问服务器
│   ├── --track cube                  # 选择要读取的 track
│   └── --json                        # 输出缓存 JSON
└── status                            # 默认等同 show；可选择先刷新
    ├── --track cube                  # 选择 track
    ├── --refresh                     # 先运行 refresh 再展示
    └── --json                        # 输出 JSON
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
