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

三者选择一个即可，不要重复引用。不要将 OpenAI 规则设置为 `DIRECT`，除非当前网络能直接访问 OpenAI。

Codex 桌面版会使用 HTTPS 和 WebSocket 连接，例如 `wss://chatgpt.com/Sampling`。
如果只开启系统 HTTP 代理但应用流量没有被 Shadowrocket 完整接管，建议开启 TUN/VPN
或增强模式，并确保本规则位于 `GEOIP`、`FINAL` 和大范围 `DIRECT` 规则之前。

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
