# Python 接口树

`ChatLinux` 的 CLI 保持薄入口；实质能力放在可 import 的 Python 函数里，便于后续 MCP、自动化脚本或其他 ChatArch 包复用。

## 包入口

```python
from chatlinux import __version__
```

## Fleet 状态接口

```python
from chatlinux.fleet import (
    init_config,
    load_config,
    refresh_track,
    load_cache,
    format_table,
    state_paths,
)
```

| 函数 | 作用 |
| --- | --- |
| `state_paths(home=None, track="cube")` | 返回 `home`、`config`、`cache_dir`、`runtime_dir`、`inventory`、`probe`、`cache`，所有默认落在同一个 ChatArch state root 下。 |
| `init_config(home=None, sample="cube", force=False)` | 初始化 `fleet.json`、cache 和 runtime 目录。 |
| `load_config(home=None)` | 读取并校验 fleet 配置。 |
| `refresh_track(home=None, track="cube", runner=subprocess.run)` | 运行 Ansible 只读刷新，归一化结果并写缓存。 |
| `load_cache(home=None, track="cube")` | 读取上一次缓存，不访问服务器。 |
| `format_table(snapshot)` | 把缓存 JSON 渲染为紧凑表格。 |
| `parse_ansible_output(output, expected_hosts=...)` | 解析 Ansible `-o` script 输出。 |

## 模块结构

```text
chatlinux
├── cli.py           # Click 入口，只做参数解析和输出
├── config.py        # ChatEnv provider
└── fleet.py         # fleet 配置、Ansible refresh、缓存和渲染逻辑
```

## 输出约定

- `refresh_track` 返回结构化 dict，写入 `cache/<track>-status.json`，并在同一个 home 下生成 `runtime/fleet-inventory.ini` 与 `runtime/fleet_probe.py`。
- `load_cache` 只读本地缓存，适合快速 shell/status 查询。
- 远端采样失败会保留在对应 host 的 `ok=false` / `error` 字段中。
- 对外输出默认不要泄漏 token、cookie、内部 Authorization header 或人员敏感信息。
