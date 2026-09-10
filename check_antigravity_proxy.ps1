<#
.SYNOPSIS
    Antigravity 本机代理与功能可用性综合诊断脚本
    Check local proxy settings and verify Google Antigravity functionality.

.DESCRIPTION
    1. 自动扫描并识别本机代理（Windows 系统代理、环境变量代理、WinHTTP 代理、本地客户端监听端口）。
    2. 检测本机 Antigravity 运行环境与核心语言服务进程。
    3. 通过代理测试 Antigravity 核心链路：
       - 出口 IP 与地理区域兼容性（检测是否处于 Gemini 允许服务区）
       - Google 账号与 OAuth 认证服务 (accounts.google.com / oauth2.googleapis.com)
       - Google Gemini / Generative Language API 模型接口 (generativelanguage.googleapis.com)
       - Google Vertex AI 企业接口 (aiplatform.googleapis.com)
       - Antigravity 官方门户与服务 (antigravity.google / gemini.google.com)
       - 开发者生态与技能扩展库 (api.github.com / registry.npmjs.org)
    4. 评估网络延迟，并给出针对终端工具（Git、CLI、Python 子代理）的配置与优化建议。

.PARAMETER Proxy
    指定要测试的代理服务器地址，如 "http://127.0.0.1:7897"。如果不指定，脚本会自动探测当前启用的代理。

.PARAMETER Direct
    强制直连测试（不使用任何代理），用于对比代理与直连差异。

.PARAMETER SetTerminalProxy
    如果检测到系统代理有效，自动在当前终端会话中设置 HTTP_PROXY / HTTPS_PROXY 环境变量。

.EXAMPLE
    .\check_antigravity_proxy.ps1
    .\check_antigravity_proxy.ps1 -Proxy "http://127.0.0.1:7897"
    .\check_antigravity_proxy.ps1 -SetTerminalProxy
#>

[CmdletBinding()]
param(
    [string]$Proxy,
    [switch]$Direct,
    [switch]$SetTerminalProxy,
    [int]$TimeoutSec = 6
)

try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

function Write-Pass([string]$text) {
    Write-Host "  [✓ 正常] " -ForegroundColor Green -NoNewline
    Write-Host $text
}

function Write-Fail([string]$text) {
    Write-Host "  [✗ 失败] " -ForegroundColor Red -NoNewline
    Write-Host $text
}

function Write-Warn([string]$text) {
    Write-Host "  [⚠ 警告] " -ForegroundColor Yellow -NoNewline
    Write-Host $text
}

function Write-Info([string]$text) {
    Write-Host "  [ℹ 信息] " -ForegroundColor Cyan -NoNewline
    Write-Host $text
}

function Write-Section([string]$title) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "  $title" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
}

function Get-RegistryProxy {
    $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    $proxyEnable = 0
    $proxyServer = ""
    $autoConfig = ""

    if (Test-Path $regPath) {
        $props = Get-ItemProperty -Path $regPath
        $proxyEnable = [int]$props.ProxyEnable
        $proxyServer = [string]$props.ProxyServer
        $autoConfig  = [string]$props.AutoConfigURL
    }

    [PSCustomObject]@{
        Enabled        = ($proxyEnable -eq 1)
        Server         = $proxyServer
        AutoConfigURL  = $autoConfig
    }
}

function Get-ListeningProxyPorts {
    $commonPorts = @(7890, 7897, 7891, 10808, 10809, 1080, 2080, 2081, 8888, 8080)
    $found = @()

    try {
        $conns = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
                 Where-Object { $_.LocalPort -in $commonPorts }
        
        foreach ($c in $conns) {
            $pName = "未知进程"
            try {
                $proc = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
                if ($proc) { $pName = $proc.ProcessName }
            } catch {}

            $addrStr = "$($c.LocalAddress)"
            $found += [PSCustomObject]@{
                Port        = $c.LocalPort
                IpAddress   = [string]$c.LocalAddress
                ProcessName = $pName
                PID         = $c.OwningProcess
            }
        }
    } catch {}

    return ,$found
}

function Get-AntigravityRuntimeInfo {
    $procs = @(Get-Process | Where-Object { $_.ProcessName -match "antigravity|language_server" })
    $agyInPath = $null
    try {
        $agyCmd = Get-Command "agy" -ErrorAction SilentlyContinue
        if ($agyCmd) { $agyInPath = $agyCmd.Source }
    } catch {}

    $appInstallDir = "$env:LOCALAPPDATA\Programs\antigravity"
    $installed = Test-Path $appInstallDir

    [PSCustomObject]@{
        Installed    = $installed
        InstallDir   = $appInstallDir
        RunningProcs = $procs
        CliInPath    = $agyInPath
    }
}

function Test-HttpEndpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$ProxyUrl,
        [int]$Timeout = 6
    )

    $proxyArgs = @()
    if ($ProxyUrl) {
        $proxyArgs = @("--proxy", $ProxyUrl)
    }

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $output = & curl.exe -s -o NUL -w "%{http_code}|%{time_total}" @proxyArgs "$Url" --max-time $Timeout 2>&1
        $sw.Stop()

        if ($LASTEXITCODE -eq 0 -and $output -match "^([0-9]{3})\|([0-9\.]+)") {
            $code = [int]$matches[1]
            $timeSec = [double]$matches[2]
            $timeMs = [int]($timeSec * 1000)

            # API 根路径返回 200, 204, 301, 302, 307, 308, 404, 400, 401, 403 均代表网络可达与 TLS 成功
            $ok = ($code -in 200, 204, 301, 302, 307, 308, 404, 400, 401, 403)
            return [PSCustomObject]@{
                Name    = $Name
                Url     = $Url
                Success = $ok
                Code    = $code
                TimeMs  = $timeMs
                Error   = $null
            }
        } else {
            return [PSCustomObject]@{
                Name    = $Name
                Url     = $Url
                Success = $false
                Code    = 0
                TimeMs  = $sw.ElapsedMilliseconds
                Error   = "请求超时或连接被重置 (ExitCode: $LASTEXITCODE)"
            }
        }
    } catch {
        $sw.Stop()
        return [PSCustomObject]@{
            Name    = $Name
            Url     = $Url
            Success = $false
            Code    = 0
            TimeMs  = $sw.ElapsedMilliseconds
            Error   = $_.Exception.Message
        }
    }
}

# ==================== 执行流程开始 ====================
Write-Host ""
Write-Host "############################################################" -ForegroundColor Cyan
Write-Host "#        Google Antigravity 本机代理与功能连通性诊断       #" -ForegroundColor Cyan
Write-Host "############################################################" -ForegroundColor Cyan
Write-Host "检测时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | 系统: Windows" -ForegroundColor Gray

# ----------------- 步骤 1: 扫描本机网络代理配置 -----------------
Write-Section "步骤 1: 扫描本机网络代理配置"

$regProxy = Get-RegistryProxy
if ($regProxy.Enabled -and $regProxy.Server) {
    Write-Pass "Windows 系统代理 (WinINet): 已启用 -> $($regProxy.Server)"
} elseif ($regProxy.AutoConfigURL) {
    Write-Warn "Windows PAC 自动脚本: $($regProxy.AutoConfigURL)"
} else {
    Write-Info "Windows 系统代理 (WinINet): 未开启 (直连模式)"
}

$envHttp  = $env:HTTP_PROXY
$envHttps = $env:HTTPS_PROXY
$envAll   = $env:ALL_PROXY

if ($envHttp -or $envHttps -or $envAll) {
    Write-Pass "终端环境变量代理已设置:"
    if ($envHttp)  { Write-Host "         HTTP_PROXY  = $envHttp" -ForegroundColor DarkGray }
    if ($envHttps) { Write-Host "         HTTPS_PROXY = $envHttps" -ForegroundColor DarkGray }
    if ($envAll)   { Write-Host "         ALL_PROXY   = $envAll" -ForegroundColor DarkGray }
} else {
    Write-Warn "终端环境变量代理: 未设置 (PowerShell/CMD 命令行默认直连)"
}

$listening = @(Get-ListeningProxyPorts)
if ($listening.Count -gt 0) {
    Write-Pass "检测到本机活跃代理端口 ($($listening.Count) 个):"
    foreach ($item in $listening) {
        Write-Host ("         端口 {0,-5} ({1,-9}) | 进程: {2} (PID: {3})" -f $item.Port, $item.IpAddress, $item.ProcessName, $item.PID) -ForegroundColor DarkCyan
    }
} else {
    Write-Info "未在 7890/7897/10808/10809 发现常见代理服务监听"
}

# 确定本次测试代理
$effectiveProxy = ""
if ($Direct) {
    $effectiveProxy = ""
    Write-Warn "测试模式: 强制直连 (Direct)"
} elseif ($Proxy) {
    $effectiveProxy = $Proxy
    Write-Info "测试模式: 使用指定代理 -> $effectiveProxy"
} elseif ($regProxy.Enabled -and $regProxy.Server) {
    $server = $regProxy.Server
    if ($server -notmatch "^https?://") { $server = "http://$server" }
    $effectiveProxy = $server
    Write-Info "测试模式: 自动采用 Windows 系统代理 -> $effectiveProxy"
} elseif ($envHttps) {
    $effectiveProxy = $envHttps
    Write-Info "测试模式: 自动采用环境变量代理 -> $effectiveProxy"
} elseif ($listening.Count -gt 0) {
    $defaultPort = $listening[0].Port
    $effectiveProxy = "http://127.0.0.1:$defaultPort"
    Write-Warn "测试模式: 系统代理未启用，自动测试本地监听端口 -> $effectiveProxy"
} else {
    $effectiveProxy = ""
    Write-Warn "测试模式: 未检测到代理，将采用直连测试"
}

# ----------------- 步骤 2: 检查本机 Antigravity 环境 -----------------
Write-Section "步骤 2: 检查本机 Antigravity 运行状态"
$agInfo = Get-AntigravityRuntimeInfo
if ($agInfo.Installed) {
    Write-Pass "Antigravity 桌面应用: 已安装 ($($agInfo.InstallDir))"
} else {
    Write-Info "Antigravity 桌面应用: 未在默认用户目录发现"
}

if ($agInfo.RunningProcs.Count -gt 0) {
    Write-Pass "Antigravity 进程运行中 ($($agInfo.RunningProcs.Count) 个活跃进程):"
    foreach ($p in $agInfo.RunningProcs) {
        $memMb = [math]::Round($p.WorkingSet64 / 1MB, 1)
        Write-Host ("         PID {0,-6} | {1,-30} | 内存占用: {2,6} MB" -f $p.Id, $p.ProcessName, $memMb) -ForegroundColor DarkCyan
    }
} else {
    Write-Info "当前系统没有正在运行的 Antigravity 进程"
}

# ----------------- 步骤 3: 连通性与功能测试 -----------------
Write-Section "步骤 3: 探测代理出口 IP 及 Antigravity 核心链路"

Write-Host "  正在查询代理出口节点地理位置..." -ForegroundColor Gray
$exitIp = "未知"
$exitLoc = "未知"
$exitColo = ""

$curlProxyArgs = @()
if ($effectiveProxy) {
    $curlProxyArgs = @("--proxy", $effectiveProxy)
}

try {
    $traceLines = & curl.exe -s @curlProxyArgs "https://cloudflare.com/cdn-cgi/trace" --max-time 6 2>$null
    if ($traceLines) {
        $traceStr = ($traceLines -join "`n")
        if ($traceStr -match "ip=([^\r\n]+)") { $exitIp = $matches[1].Trim() }
        if ($traceStr -match "loc=([^\r\n]+)") { $exitLoc = $matches[1].Trim() }
        if ($traceStr -match "colo=([^\r\n]+)") { $exitColo = $matches[1].Trim() }
    }
} catch {}

# 常见地区中文映射
$countryNames = @{
    "KR" = "韩国 (South Korea)"
    "JP" = "日本 (Japan)"
    "SG" = "新加坡 (Singapore)"
    "US" = "美国 (United States)"
    "HK" = "香港 (Hong Kong)"
    "TW" = "台湾 (Taiwan)"
    "GB" = "英国 (United Kingdom)"
    "DE" = "德国 (Germany)"
    "CN" = "中国大陆 (China)"
    "RU" = "俄罗斯 (Russia)"
}
$locFriendly = if ($countryNames.ContainsKey($exitLoc)) { $countryNames[$exitLoc] } else { $exitLoc }

$unsupportedRegions = @("CN", "RU", "IR", "KP", "BY", "SY", "CU")
$partiallySupported = @("HK")

Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "  出口 IP 地址:   " -NoNewline
Write-Host "$exitIp" -ForegroundColor Cyan
Write-Host "  出口地理位置:   " -NoNewline
Write-Host "$locFriendly " -ForegroundColor Cyan -NoNewline
if ($exitColo) { Write-Host "(数据中心: $exitColo) " -ForegroundColor DarkGray -NoNewline }

if ($exitLoc -in $unsupportedRegions) {
    Write-Host "[受限地区]" -ForegroundColor Red
    Write-Warn "当前节点位于受限地区 ($exitLoc)，Google Gemini 系列 API 通常会屏蔽来自该地区的请求！"
    Write-Warn "建议切换至 日本 (JP)、新加坡 (SG)、韩国 (KR) 或 美国 (US) 节点。"
} elseif ($exitLoc -in $partiallySupported) {
    Write-Host "[部分受限]" -ForegroundColor Yellow
    Write-Warn "香港 (HK) 节点部分 Google AI 服务可能受限，若遇到调用报错，请换用 US/JP/SG 节点。"
} else {
    Write-Host "[支持良好]" -ForegroundColor Green
}
Write-Host "  ------------------------------------------------------------" -ForegroundColor DarkGray

$testTargets = @(
    @{ Name = "Google 账号体系 (OAuth/登录)"; Url = "https://accounts.google.com" },
    @{ Name = "Google OAuth 令牌刷新通道";   Url = "https://oauth2.googleapis.com" },
    @{ Name = "Gemini API (语言模型核心接口)"; Url = "https://generativelanguage.googleapis.com" },
    @{ Name = "Google Vertex AI 企业云平台";   Url = "https://aiplatform.googleapis.com" },
    @{ Name = "Antigravity 官方门户与服务";   Url = "https://antigravity.google" },
    @{ Name = "Gemini 官方 Web 服务应用";     Url = "https://gemini.google.com" },
    @{ Name = "GitHub API (扩展/Skills/更新)";Url = "https://api.github.com" },
    @{ Name = "npm 官方镜像 (前端扩展源)";     Url = "https://registry.npmjs.org" }
)

Write-Host "`n  开始测试各项关键服务连通性..." -ForegroundColor Gray
$results = @()
foreach ($target in $testTargets) {
    $res = Test-HttpEndpoint -Name $target.Name -Url $target.Url -ProxyUrl $effectiveProxy -Timeout $TimeoutSec
    $results += $res

    $timeColor = if ($res.TimeMs -lt 800) { "Green" } elseif ($res.TimeMs -lt 1800) { "Yellow" } else { "Red" }

    if ($res.Success) {
        Write-Host "  [✓ 通过] " -ForegroundColor Green -NoNewline
        Write-Host ("{0,-32} " -f $res.Name) -NoNewline
        Write-Host ("{0,5} ms" -f $res.TimeMs) -ForegroundColor $timeColor -NoNewline
        Write-Host " (HTTP $($res.Code))" -ForegroundColor DarkGray
    } else {
        Write-Host "  [✗ 失败] " -ForegroundColor Red -NoNewline
        Write-Host ("{0,-32} " -f $res.Name) -NoNewline
        Write-Host "$($res.Error)" -ForegroundColor DarkRed
    }
}

# ----------------- 步骤 4: 评估结论与实用建议 -----------------
Write-Section "步骤 4: 综合评估与配置建议"

$passedCount = @($results | Where-Object { $_.Success }).Count
$totalCount = $results.Count
$percent = [math]::Round(($passedCount / $totalCount) * 100)

Write-Host "核心服务连通通过率: " -NoNewline
if ($percent -eq 100) {
    Write-Host "$passedCount / $totalCount (100%)" -ForegroundColor Green
} elseif ($percent -ge 75) {
    Write-Host "$passedCount / $totalCount ($percent%)" -ForegroundColor Yellow
} else {
    Write-Host "$passedCount / $totalCount ($percent%)" -ForegroundColor Red
}

if ($passedCount -eq $totalCount -and $exitLoc -notin $unsupportedRegions) {
    Write-Host ""
    Write-Host "【综合评估结论: 极佳 (PASS)】" -ForegroundColor Green
    Write-Host "  当前本机代理环境完全满足 Google Antigravity 的运行需求！" -ForegroundColor Green
    Write-Host "  ✔ Google 账号与授权认证稳定畅通"
    Write-Host "  ✔ Gemini 大模型推理与 Vertex AI 接口响应迅速"
    Write-Host "  ✔ 官方服务、扩展技能库及开发生态连接正常"
} elseif ($passedCount -ge 5) {
    Write-Host ""
    Write-Host "【综合评估结论: 基本可用 (WARNING)】" -ForegroundColor Yellow
    Write-Host "  核心链路已连通，但有部分周边服务超时或地区受限，可能会影响部分扩展功能。" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "【综合评估结论: 不可用 (FAIL)】" -ForegroundColor Red
    Write-Host "  核心接口连接失败，Antigravity 无法正常进行 AI 推理或登录授权。" -ForegroundColor Red
}

Write-Host "`n【实用优化指引】:" -ForegroundColor Cyan

# 提示 1: 终端环境变量配置
if ($effectiveProxy -and (-not $envHttp -or -not $envHttps)) {
    Write-Host "  1. 终端命令行代理设置:" -ForegroundColor White
    Write-Host "     Windows 系统代理仅对浏览器及 Electron 界面直接生效。" -ForegroundColor Gray
    Write-Host "     若要让终端工具 (git, curl, python, uv, node) 也走代理，请在终端中运行:" -ForegroundColor Gray
    Write-Host "     `$env:HTTP_PROXY = `"$effectiveProxy`"; `$env:HTTPS_PROXY = `"$effectiveProxy`"" -ForegroundColor Yellow

    if ($SetTerminalProxy) {
        $env:HTTP_PROXY = $effectiveProxy
        $env:HTTPS_PROXY = $effectiveProxy
        $env:ALL_PROXY = $effectiveProxy
        Write-Pass "已按 -SetTerminalProxy 参数为当前 PowerShell 注入代理环境变量！"
    }
} else {
    Write-Host "  1. 终端环境变量代理状态: 已就绪" -ForegroundColor Gray
}

# 提示 2: TUN 虚拟网卡模式建议
$clashClient = $listening | Where-Object { $_.ProcessName -match "verge|clash|mihomo|sing-box" }
if ($clashClient) {
    Write-Host "  2. 代理客户端模式推荐:" -ForegroundColor White
    Write-Host "     检测到正在运行 $($clashClient[0].ProcessName)。强烈推荐在客户端设置中开启【TUN 模式】(虚拟网卡)。" -ForegroundColor Gray
    Write-Host "     开启 TUN 模式后，系统级所有命令行、Git、子代理工具均可免配置无缝透明翻墙。" -ForegroundColor Gray
}

Write-Host ""