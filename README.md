# OpenAI Shadowrocket Rules

适用于 ChatGPT 网页版、ChatGPT 桌面版、Codex 桌面版、OpenAI API、Sora 和
Advanced Voice 的代理分流规则。

核心域名来自
[`v2fly/domain-list-community`](https://github.com/v2fly/domain-list-community/blob/master/data/openai)，
并补充 OpenAI 官方网络建议中的登录、验证码、功能开关、错误上报、支付、WorkOS
和 Cloudflare Challenge 等第三方依赖。仓库每周自动更新。

## Shadowrocket

完整兼容版（推荐）应放在 `GEOIP` 和 `FINAL` 前，并将 `PROXY` 替换为你的节点或策略组名称：

```ini
RULE-SET,https://raw.githubusercontent.com/DDcat2025/openai-shadowrocket-rules/main/rule/Shadowrocket/OpenAI/OpenAI.list,PROXY
```

如果不希望 OpenAI 规则影响共用第三方服务，可改用核心版：

```ini
RULE-SET,https://raw.githubusercontent.com/DDcat2025/openai-shadowrocket-rules/main/rule/Shadowrocket/OpenAI/OpenAI_Core.list,PROXY
```

仅使用域名集合时：

```ini
DOMAIN-SET,https://raw.githubusercontent.com/DDcat2025/openai-shadowrocket-rules/main/rule/Shadowrocket/OpenAI/OpenAI_Domain.list,PROXY
```

优先选择 RULE-SET 完整版或精确依赖版。核心 DOMAIN-SET 不能表达关键词规则，也不包含完整第三方依赖；不能把它视为完整版的等价替代。不要将 OpenAI 规则设置为 `DIRECT`，除非当前网络能直接访问 OpenAI。

Codex 桌面版会使用 HTTPS 和 WebSocket 连接，例如 `wss://chatgpt.com/Sampling`。
如果只开启系统 HTTP 代理但应用流量没有被 Shadowrocket 完整接管，建议开启 TUN/VPN
或增强模式，并确保本规则位于 `GEOIP`、`FINAL` 和大范围 `DIRECT` 规则之前。

### Codex 内置生图

Codex Desktop 使用 ChatGPT 登录态调用内置图像生成服务，请求入口为
`https://chatgpt.com/backend-api/codex/images/generations`。本规则通过
`DOMAIN-SUFFIX,chatgpt.com` 覆盖请求通道，并通过
`DOMAIN-SUFFIX,oaiusercontent.com` 覆盖常见的生成结果资源域名，因此无需为
Image 2 单独添加模型域名。

## Mihomo / Clash Meta

```yaml
rule-providers:
  openai:
    type: http
    behavior: classical
    url: https://raw.githubusercontent.com/DDcat2025/openai-shadowrocket-rules/main/rule/Mihomo/OpenAI/OpenAI.yaml
    path: ./ruleset/openai.yaml
    interval: 86400

rules:
  - RULE-SET,openai,PROXY
```

## 文件

- `OpenAI.list`：完整兼容版，包含 OpenAI 核心域名及必要的第三方依赖。
- `OpenAI_Core.list`：仅 OpenAI 核心服务、CDN 和语音域名。
- `OpenAI_Domain.list`：Shadowrocket `DOMAIN-SET` 核心域名格式。
- `OpenAI.yaml`：Mihomo classical rule-provider 完整兼容版。
- `data/openai-domains.txt`：每行一个核心域名。

## 注意

- OpenAI 服务具有地区限制，代理节点所在地区必须受支持。
- 完整兼容版包含 Auth0、Arkose Labs、Cloudflare、Datadog、Statsig、Sentry、Stripe、WorkOS 等共享服务域名，可能同时影响使用这些服务的其他应用。
- IP、应用内硬编码地址和 DNS 劫持不属于本域名规则覆盖范围。

## 2026-10-12 覆盖与格式修复

保留原有 OpenAI.list 完整兼容版，并补入当前官方明确列出的 WorkOS、设备验证、错误上报、WebSocket 等主机。新增：

- `OpenAI_Precise.list` / `OpenAI_Precise.yaml`：上游核心 + 官方点名依赖，不加入旧版额外的整个 Cloudflare / Datadog / Stripe 等父域，便于减少跨应用影响。核心源本身仍可能含共享语音/统计域。
- `OpenAI_Voice.list` / `OpenAI_Voice.yaml`：官方语音服务器 IP 快照，可选配合主规则；UDP 3478 / TCP 443 是否可用取决于节点和网络。
- `OpenAI_Keyword.list`：核心动态 Azure WebPubSub 名称的关键词补充。它比上游正则更宽；Shadowrocket 和 Mihomo 的可移植输出沿用该近似并在此明确说明。
- 修复 OpenAI_Domain.list：full: 精确主机保持精确，不再错误扩大成整个子域后缀。后缀项仍使用前导点。
- 官方补充保存在 `data/official-dependencies.txt`，每周重建不会丢失。语音 IP 源是 [官方 JSON](https://openai.com/chatgpt-voice.json)。

推荐精确依赖版（替换完整兼容版，不叠加）：

```ini
RULE-SET,https://raw.githubusercontent.com/DDcat2025/openai-shadowrocket-rules/main/rule/Shadowrocket/OpenAI/OpenAI_Precise.list,OPENAI
# 可选语音 IP，放在 GEOIP 前
RULE-SET,https://raw.githubusercontent.com/DDcat2025/openai-shadowrocket-rules/main/rule/Shadowrocket/OpenAI/OpenAI_Voice.list,OPENAI
```

OPENAI 是需要在客户端手动绑定的策略组。[完整分流顺序和其他服务](https://github.com/DDcat2025/shadowrocket-routing-rules)。源覆盖不等同于每个 App、下载、上传及实时语音都已在真机验收。
