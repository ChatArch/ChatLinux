# Changelog

## 0.2.2 - 2026-08-21

### Changed

- Replace the local Click tree renderer with ChatStyle's shared `add_tree_option()` runtime.
- Keep `chatlinux` as the canonical tree root, show parameter signatures in `--tree`, and add signature-free `--tree-brief` output.
- Raise dependency bounds to `chatstyle>=0.2.0,<0.3.0` and `chatenv>=0.2.10,<0.3.0`.

## 0.2.1 - 2026-08-11

### Added

- Add top-level `chatlinux --tree` generated from the registered Click command surface.
- Add tests that lock `--help` / `--tree` and the visible `fleet init/refresh/show/status` command tree.

### Changed

- Sync the zh/en CLI tree docs from runtime `render_cli_tree()` output.
- Tighten docs optional dependency bounds to the strict-build-safe `mkdocs-material<9.7` window.
- Raise the ChatEnv dependency floor to the currently released `0.2.4` line.

## 0.2.0 - 2026-08-05

### Added

- 新增 `chatlinux fleet` CLI：`init` 初始化 `.cube` track 配置，`refresh` 通过 Ansible 只读刷新常规指标并写缓存，`show` / `status` 快速读取上一次缓存。
- 新增 `chatlinux.fleet` 可 import Python API，用于 fleet 配置、Ansible 输出解析、缓存读写和表格渲染。
- 新增 fleet quick start、CLI 树、能力地图和 Python 接口树文档。
- 文档明确 fleet 默认状态根为 `CHATLINUX_HOME` > `$CHATARCH_HOME/chatlinux` > `~/.chatarch/chatlinux`，并列出 `fleet.json`、`cache/` 和 refresh 生成的 `runtime/` inventory/probe。
- `chatlinux fleet init --json` 现在回显完整 `state_paths`，便于 CI/验收确认默认数据路径在 ChatArch 内部。

### Changed

- README 和 MkDocs 首页改为以 fleet 状态缓存为当前首个业务能力入口。
- Quick Start 增加 Material `grid cards` 流程入口，对齐 ChatArch / ChatTea 参考形态的非线性文档结构。
- 将 docs extra 的 `mkdocs-material` 上限对齐到 ChatArch MkDocs skill 推荐的 `<10.0`。
- Preview Docs workflow 从 `mkdocs.yml` 的 `site_url` 派生 `/dev/` URL，避免文档域名在 workflow 中重复定义。
- ChatEnv provider storage namespace 统一为小写 `chatlinux`。

### Fixed

- 修复 `systemctl --failed` 输出以 `●` 开头时误把 bullet 解析为 unit 名的问题。
- 统一 fleet 状态路径为 `state_paths()` 单一来源，避免 config/cache/runtime/probe/inventory 路径散落。

## 0.1.0 - 2026-08-05

### Added

- 发布 `0.1.0`：ChatLinux 包基础 scaffold、CLI 版本输出、ChatEnv provider、MkDocs 文档骨架与 GitHub Actions/OIDC 发布工作流。
