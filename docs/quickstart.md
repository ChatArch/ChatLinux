# 快速开始

这个页面给出 ChatLinux 当前最小可用的 fleet 状态查看流程：初始化 track 配置、刷新一次 Ansible 缓存、再从缓存快速查看。

## 流程入口

<div class="grid cards" markdown>

- **安装与验证**

    安装包并确认 `chatlinux --version`、`chatlinux fleet --help` 可用。

    [跳到安装](#install-verify)

- **初始化内部状态目录**

    写入 `fleet.json`，并准备 `cache/`、`runtime/`，默认都在 `~/.chatarch/chatlinux/`。

    [跳到初始化](#init-cube-track)

- **刷新远端状态**

    通过 Ansible 只读生成 inventory/probe、采集常规公共指标，并写入本地缓存。

    [跳到刷新](#refresh-status)

- **读取缓存 / 安全边界**

    `show` / `status` 默认只读缓存；需要远端采样时显式使用 `refresh` 或 `status --refresh`。

    [跳到查看缓存](#read-cache)

</div>

## 安装与验证 {#install-verify}

```bash
pip install ChatLinux
chatlinux --version
chatlinux fleet --help
```

开发 checkout 中可用：

```bash
python -m pip install -e ".[dev,docs]"
PYTHONPATH=src python -m chatlinux.cli fleet --help
```

## 初始化 `.cube` track {#init-cube-track}

默认状态目录在 ChatArch home 内部：优先 `CHATLINUX_HOME`，否则 `$CHATARCH_HOME/chatlinux`，再否则 `~/.chatarch/chatlinux/`。第一次使用先写入 sample 配置：

```bash
chatlinux fleet init --sample cube --json
```

JSON 输出会包含完整 `state_paths`，用于确认所有本地状态文件都在同一个 ChatArch state root 下。这会创建或使用：

```text
~/.chatarch/chatlinux/fleet.json
~/.chatarch/chatlinux/cache/
~/.chatarch/chatlinux/runtime/
```

`runtime/` 保存 refresh 生成的 `fleet-inventory.ini` 和 `fleet_probe.py`。这些文件仍在 ChatArch home 内部，不写入 `/etc`、`/usr`、系统服务目录或任务仓库。

如果要在任务目录或 CI 中隔离状态，用 `--home` 覆盖：

```bash
chatlinux fleet --home ./playground/chatlinux-home init --sample cube --json
```

## 刷新状态 {#refresh-status}

`refresh` 会读取 track 配置，生成 Ansible inventory 和只读 probe 脚本，然后运行 Ansible 采集常规公共指标并写缓存。

```bash
chatlinux fleet refresh --track cube
```

机器可读输出：

```bash
chatlinux fleet refresh --track cube --json
```

当前 sample track 默认通过：

```text
uvx --from ansible-core ansible
```

并使用 `.cube` 巡检验证过的远端 Python：

```text
/home/zhihong/.chatarch/venv/bin/python
```

## 查看上一次缓存 {#read-cache}

查看缓存不会访问服务器，适合快速 shell 查询：

```bash
chatlinux fleet show --track cube
chatlinux fleet status --track cube
```

需要先刷新再展示时：

```bash
chatlinux fleet status --track cube --refresh
```

## 当前采集指标

MVP 只采集常规、容易、公共的只读指标：

- hostname、采样时间、uptime、CPU count、load average；
- memory total/available、swap total/used；
- `df -P -T` 文件系统容量；
- `nvidia-smi` 可用时的 GPU 数量、型号、显存和利用率；
- `systemctl --failed` 失败 unit 列表。

## 安全边界

- 不执行 sudo。
- 不清理、不重启、不修复远端服务。
- `show` / `status` 默认只读缓存；只有 `refresh` 或 `status --refresh` 会访问服务器。
- 当前版本不采集 SMART/NVMe 寿命；需要明确 helper 或只读 sudo 授权后再扩展。
