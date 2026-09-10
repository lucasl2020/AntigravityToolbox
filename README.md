# Antigravity 综合管理工具箱 (Antigravity Toolbox)

专为 **Google Antigravity** 打造的高颜值全功能桌面可视化工作台，集 **网络连通与代理诊断**、**全中文界面汉化 (antigravity2-cn)**、**免 TUN 强制代理注入 (antigravity-proxy)** 以及 **每次启动自动检测更新与开源资源热拉取** 于一体。

采用 **Fluent 2 / Apple Clean Slate 现代化明亮浅色主题**，高分屏自适应，内置 4 大核心指标卡片、Mac 风格三色红黄绿控制台，架构全面优化实现 **0.3 秒瞬间秒开**。

---

## ⚡ 启动与使用方式

### 方式 1：双击绿色便携版（免环境极速秒开，最推荐 ⭐⭐⭐⭐⭐）
程序采用独立便携分发架构，双击根目录快捷启动文件即可瞬间打开：
👉 **`启动工具箱.bat`**  
或直接进入目录双击可执行文件：
👉 **`dist\AntigravityToolbox\AntigravityToolbox.exe`**

> **为什么启动如此迅速？**  
> 彻底摒弃了传统单文件打包每次冷启动向系统临时目录 `%TEMP%` 解压 150MB 文件与触发 Windows Defender 防病毒扫描带来的 5~10 秒卡顿。便携版在本地直接就绪运行，**0.3 秒内瞬间开窗**！可在任何未安装 Python、Node 或 Git 的纯净 Windows 10/11 电脑上即拷即用。

---

### 方式 2：自己重新执行打包（一键生成最新独立分发包）
如后续修改了代码、字典或更新了依赖，直接双击：
👉 **`build_exe.bat`**  
或进入 `scripts\` 目录执行：
👉 **`scripts\build_exe.bat`**

> 脚本将自动调用 PyInstaller 编译生成 `dist\AntigravityToolbox\`，并将最新的 `resources\` 资源包完整同步至可执行文件同级目录，一键完成标准化分发。

---

### 方式 3：Python 源码开发模式运行
在已安装 Python 依赖的环境中，双击：
👉 **`run_gui.bat`**  
或在终端执行：
```bash
python src/app.py
```

---

## 📁 规范化项目目录结构

整个项目遵循现代企业级桌面软件架构，将源代码、核心业务、UI组件、运维脚本与离线资源清晰分离：

```
check-antigravity-proxy/
├── dist/
│   └── AntigravityToolbox/        # 【独立免环境绿色分发包】直接拷走即可运行
│       ├── AntigravityToolbox.exe # 极速秒开主程序 (< 0.5s)
│       ├── resources/             # 核心资源库 (与 exe 永远保持同级)
│       │   ├── versions.json      # 记录两开源项目本地当前版本与 Commit SHA
│       │   ├── proxy_injector/    # 免 TUN 代理依赖 (version.dll, config.json)
│       │   └── localization/      # 汉化依赖 (localization_engine.js, dicts/)
│       ├── 启动工具箱.bat         # 目录内快捷启动
│       └── _internal/             # PySide6 与 Python 独立运行时库
├── src/                           # 【核心源代码目录】
│   ├── app.py                     # 程序主入口 (极速延迟装载)
│   ├── core/                      # 底层核心业务层
│   │   ├── paths.py               # 统一跨环境路径解析 (支持源码与打包运行)
│   │   ├── detector.py            # 网络、代理、出口IP与核心端点诊断
│   │   ├── localizer.py           # ASAR 汉化注入引擎与官方原版一键还原
│   │   ├── injector.py            # 免 TUN 强制代理注入与配置文件管理
│   │   └── updater.py             # GitHub 在线更新检查与资源增量热拉取
│   └── ui/                        # 现代化用户界面层
│       ├── main_window.py         # 主窗口、侧栏导航与更新通告横幅
│       ├── styles.py              # Fluent 2 / Apple Slate 现代明亮浅色主题
│       ├── widgets/               # 高颜值可复用自定义组件
│       │   ├── stat_card.py       # 现代化指标统计卡片 (4 卡片组)
│       │   └── terminal_box.py    # Mac 风格三色交通灯拟物日志控制台
│       ├── tab_detector.py        # 诊断面板
│       ├── tab_localizer.py       # 汉化管理面板
│       ├── tab_injector.py        # 免 TUN 代理注入面板
│       └── tab_updater.py         # 开源项目同步与热打包面板
├── resources/                     # 开发/模板资源库 (与 exe 同级放置)
├── scripts/                       # 【构建与自动化脚本】
│   ├── build.py                   # 独立打包 Python 自动化脚本
│   ├── build_exe.bat              # 双击打包批处理
│   └── run_gui.bat                # 源码启动批处理
├── 启动工具箱.bat                 # 根目录极速秒开入口
├── build_exe.bat                  # 根目录一键打包入口
├── run_gui.bat                    # 根目录开发运行入口
├── requirements.txt               # Python 依赖清单
└── README.md                      # 项目说明文档
```

---

## 🎨 界面与体验升级亮点

1. **秒级开窗架构**：
   - 界面先于逻辑绘制，主窗口 0.1s 瞬间呈现，耗时任务（网络探测、更新轮询）全部推入异步子线程延迟调度。
2. **纯粹浅色系现代美学**：
   - 全面抛弃沉闷暗黑主题，采用 `#f8fafc` 典雅 Slate 浅色基底配合纯白卡片面板与柔和边框。
3. **4 大核心指标卡片组 (StatCard)**：
   - 🛰️ **代理通道**：实时展示当前生效的代理地址与协议状态。
   - 🌍 **物理出口 / 地区**：展示公网出口 IP、所属国家/地区及 Gemini 准入评估。
   - 🇨🇳 **界面汉化状态**：指示是否已完成 `app.asar` 增强汉化或处于官方英文状态。
   - ⚡ **免 TUN 注入状态**：指示 `version.dll` 进程拦截挂载情况。
4. **Mac 风格拟物控制台 (TerminalBox)**：
   - 顶部还原 macOS 🔴 🟡 🟢 三色交通灯微交互，支持等宽代码高亮、平滑滚动、一键复制与清空。

---

## ✨ 四大功能面板详解

### 1. 📡 网络与代理全景诊断
- **多维度本地扫描**：自动读取 Windows 注册表 WinINet 系统代理、环境变量 (`HTTP_PROXY`)、本地活跃代理端口 (7897/7890 等)。
- **智能出口评估**：出口 IP 与地理区域自动研判，自动识别合规地区（韩国 KR、日本 JP、美国 US、新加坡 SG 标绿，受限地区如 CN、RU 自动警示）。
- **8 大核心服务链路探针**：并发测试 Google 账号体系、OAuth 刷新、Gemini API、Vertex AI、Antigravity 门户、Gemini Web、GitHub API、npm 镜像源，显示毫秒级延迟与 HTTP 状态码。
- **一键配置终端**：支持一键将检测到的代理导出为 PowerShell 环境变量命令。

### 2. 🌐 界面全中文汉化（基于 `qqxpee/antigravity2-cn`）
- 基于 Electron ASAR 包动态注入，深度汉化系统菜单、托盘、界面文案与设置面板。
- 支持 3 种品牌显示方式：保持原版英文标题（推荐）、隐藏品牌名、完全汉化为「反重力」；支持简体中文 (zh-CN) 与繁体中文 (zh-TW)。
- 提供【一键安装汉化】与【一键无痕还原官方英文原版】（自动从 `app.asar.bak` 恢复），支持完成后自动重启客户端。

### 3. ⚡ 免 TUN 强制代理注入（基于 `yuaotian/antigravity-proxy`）
- 通过 `version.dll` 动态库劫持与内存级流量拦截，强制让 Antigravity 及其核心语言服务 `language_server_windows_x64.exe`、`node.exe` 走指定代理通道。
- **无需系统开启全局 TUN 模式**，精准代理指定目标进程。
- 支持协议（SOCKS5 / HTTP）、主机与端口自定义，支持一键探测并填入本地活跃端口。
- 提供【一键注入生效】与【一键安全卸载】。

### 4. 🔄 启动自动检测更新与资源热打包
- 每次打开应用时，后台自动异步向 GitHub 查询：
  - `yuaotian/antigravity-proxy` 最新 Release（当前为 v2.4）
  - `qqxpee/antigravity2-cn` 最新翻译提交
- 检测到新版本时，主界面顶部弹出更新横幅；点击按钮可一键下载最新资源并直接热打包进可执行文件同级的 `resources/` 库中。

---

## 💡 常见问题与核心机制 (FAQ)

### Q1：代理地址是自动识别还是必须手动输入？
**答：完全全自动识别！绝大多数情况下您完全不需要手动输入任何内容。**
- **网络诊断面板**：启动时自动扫描本地代理客户端活跃监听端口（如 `7897`, `7890`, `10808`, `10809` 等）、Windows 系统代理与环境变量，自动填入 `http://127.0.0.1:7897`。即使留空，后台诊断也默认全自动嗅探。
- **免 TUN 注入面板**：未注入时会自动探测并填入当前检测到的活跃端口（如 `7897`），同时界面配有 **`⚡ 填入活跃端口`** 按钮，随时一键抓取最新活跃端口；已注入时会自动回显保存的配置。
- **何时才需手动输入？**：仅当您需要指定局域网其他机器的代理、远程代理或非常规自定义端口时，才需手动敲入修改。

### Q2：使用汉化或注入免 TUN 代理后，退出工具箱/关掉 Antigravity/电脑重启后还会一直生效吗？
**答：永久生效！本工具箱完全不需要在后台常驻运行，操作完成后随手关闭即可。**
- **🌐 界面汉化**：属于**物理文件修改**。汉化引擎直接将字典打包装入 Antigravity 安装目录的 `resources\app.asar` 中。退出工具箱、关闭 Antigravity 或电脑重启，打开客户端**始终保持中文**。只有在工具箱内点击「一键无痕还原官方英文原版」或 Google 官方发布大版本更新覆盖时才会恢复英文（重新点一次一键汉化即可）。
- **⚡ 免 TUN 代理注入**：属于 **Windows 底层 DLL 挂载机制**。将 `version.dll` 和 `config.json` 部署至 Antigravity 根目录。Antigravity 启动时 Windows 会自动优先加载该 DLL 并在内存中将核心 AI 进程流量拦截至代理端口。**工具箱只是安装/卸载管理器**，配置完成后立即退出工具箱完全不影响代理，重启电脑后依然自动生效。只有在工具箱中点击「一键卸载代理」才会移除。
- **📡 强制直连**：**仅是工具箱内的诊断测试开关**。仅影响当次诊断测试时是否跳过代理直连 Google 端点，不会改写系统网络，更不会改变 Antigravity 的运行网络。

