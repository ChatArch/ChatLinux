<div align="center">
    <a href="https://pypi.python.org/pypi/ChatLinux">
        <img src="https://img.shields.io/pypi/v/ChatLinux.svg" alt="PyPI version" />
    </a>
    <a href="https://github.com/ChatArch/ChatLinux/actions/workflows/ci.yml">
        <img src="https://github.com/ChatArch/ChatLinux/actions/workflows/ci.yml/badge.svg" alt="Tests" />
    </a>
    <a href="https://arch.gh.wzhecnu.cn/ChatLinux/">
        <img src="https://img.shields.io/badge/docs-mkdocs-blue.svg" alt="Documentation" />
    </a>
</div>

<div align="center">

[英文版](README.en.md) | [简体中文](README.md)
</div>

# ChatLinux

ChatArch Linux 运维包。当前首个业务能力是 fleet 状态缓存 CLI：用 ChatArch 内部配置 track 服务器，通过 Ansible 刷新常规公共指标，并从本地缓存快速查看状态。

文档入口：<https://arch.gh.wzhecnu.cn/ChatLinux/>

按场景选择文档：

| 场景 | 文档 |
| --- | --- |
| 第一次安装、初始化 `.cube` track、刷新/查看缓存 | [快速开始](docs/quickstart.md) |
| 查看当前真实 CLI 命令树和 shell 用法 | [CLI 树](docs/cli-tree.md) |
| 校对当前包有哪些一等能力和边界 | [能力地图](docs/capability-map.md) |
| 从 Python 代码调用包能力 | [接口树](docs/interface-tree.md) |

## 快速开始

```bash
pip install ChatLinux
chatlinux --version
chatlinux fleet init --sample cube
chatlinux fleet refresh --track cube
chatlinux fleet show --track cube
```

开发 checkout 中可用：

```bash
pip install -e ".[dev,docs]"
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m chatlinux.cli fleet --help
```

## Fleet 配置与缓存

默认本地状态根是一个 ChatArch 内部路径：优先使用 `CHATLINUX_HOME`，否则使用 `$CHATARCH_HOME/chatlinux`，再否则回落到 `~/.chatarch/chatlinux`。默认落点包括：

```text
~/.chatarch/chatlinux/fleet.json
~/.chatarch/chatlinux/cache/<track>-status.json
~/.chatarch/chatlinux/runtime/fleet-inventory.ini
~/.chatarch/chatlinux/runtime/fleet_probe.py
```

其中 `runtime/` 只保存 refresh 时生成的 Ansible inventory 和只读 probe；它仍在 ChatArch home 内部，不写入 `/etc`、`/usr`、系统服务目录或任务仓库。ChatEnv provider namespace 也使用小写 `chatlinux`，未来 ChatEnv 托管值同样归入 ChatArch home，不在工作区散落文件。

`chatlinux fleet init --json` 会回显完整 `state_paths`，用于验收 config/cache/runtime 等本地数据落点是否仍在同一个 state root 下。

任务目录或 CI 中可用 `--home` 隔离：

```bash
chatlinux fleet --home ./playground/chatlinux-home init --sample cube --json
chatlinux fleet --home ./playground/chatlinux-home status --track cube --refresh
```

## 安全边界

- `show` / `status` 默认只读本地缓存；`refresh` 和 `status --refresh` 才会访问服务器。
- 当前 MVP 只采集常规公共指标：CPU/load、内存、swap、文件系统、GPU 可用信息和 failed systemd units。
- 不执行 sudo，不清理、不重启、不修复远端服务。

## 命令行规范

这个包依赖 `chatstyle>=0.1.0,<0.2.0` 和 `chatenv>=0.2.4,<0.3.0`。新增命令应优先使用：

- `CommandSchema` / `CommandField` 描述输入。
- `add_interactive_option()` 提供统一 `-i/-I`。
- `resolve_command_inputs()` 统一缺参补问、默认值、TTY 与校验。
- 默认保留 `config.py` 和 `chatenv.configs` 入口点，使包可被 ChatEnv 发现。

## 目录结构

- `src/`：包源码
- `tests/`：代码测试与 CLI 测试
- `docs/`：长期维护文档，由 mkdocs 构建

## 开发说明

扩展包前，先阅读 `DEVELOP.md` 和 `AGENTS.md`。
