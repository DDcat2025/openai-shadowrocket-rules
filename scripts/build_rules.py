from __future__ import annotations

import argparse
import ipaddress
import json
import subprocess
from pathlib import Path


EXTRA_EXACT = {
    "humb.apple.com",
    "openai-api.arkoselabs.com",
    "static.cloudflareinsights.com",
}

EXTRA_SUFFIXES = {
    "algolia.net",
    "api.statsig.com",
    "auth0.com",
    "browser-intake-datadoghq.com",
    "client-api.arkoselabs.com",
    "cloudflare.com",
    "datadoghq.com",
    "events.statsigapi.net",
    "featuregates.org",
    "imgix.net",
    "intercom.io",
    "intercomcdn.com",
    "launchdarkly.com",
    "openaimerge.com",
    "segment.io",
    "sendgrid.net",
    "sentry.io",
    "statsig.com",
    "statsigapi.net",
    "stripe.com",
    "workos.com",
    "workoscdn.com",
}


def parse(data_file: Path) -> tuple[set[str], set[str], set[str]]:
    suffixes: set[str] = set()
    exact: set[str] = set()
    keywords: set[str] = set()
    for raw in data_file.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        value = line.split()[0]
        if value.startswith("full:"):
            exact.add(value.removeprefix("full:").lower())
        elif value.startswith("regexp:"):
            if "chatgpt-async-webps-prod-" in value:
                keywords.add("chatgpt-async-webps-prod-")
            else:
                raise ValueError(f"Unsupported regexp rule: {value}")
        elif value.startswith("include:"):
            raise ValueError(f"Unexpected include rule: {value}")
        else:
            suffixes.add(value.lower())
    return suffixes, exact, keywords


def official_rules() -> set[str]:
    rules: set[str] = set()
    for raw in Path("data/official-dependencies.txt").read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        kind, domain = line.split(":", 1)
        if kind not in {"suffix", "full"} or not domain or any(c in domain for c in " ,/*"):
            raise ValueError(f"Invalid official dependency: {line}")
        rules.add(f"{'DOMAIN-SUFFIX' if kind == 'suffix' else 'DOMAIN'},{domain.lower()}")
    return rules


def write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path, help="domain-list-community data directory")
    parser.add_argument("--repo", type=Path, help="domain-list-community repository")
    args = parser.parse_args()

    suffixes, exact, keywords = parse(args.data / "openai")
    commit = "unknown"
    if args.repo:
        commit = subprocess.check_output(
            ["git", "-C", str(args.repo), "rev-parse", "HEAD"], text=True
        ).strip()

    header = [
        "# NAME: OpenAI",
        "# AUTHOR: DDcat2025",
        "# REPO: https://github.com/DDcat2025/openai-shadowrocket-rules",
        "# SOURCE: https://github.com/v2fly/domain-list-community",
        f"# SOURCE-COMMIT: {commit}",
    ]
    core_rules = (
        [f"DOMAIN-SUFFIX,{domain}" for domain in sorted(suffixes)]
        + [f"DOMAIN,{domain}" for domain in sorted(exact)]
        + [f"DOMAIN-KEYWORD,{keyword}" for keyword in sorted(keywords)]
    )
    extra_rules = {
        *[f"DOMAIN-SUFFIX,{domain}" for domain in EXTRA_SUFFIXES],
        *[f"DOMAIN,{domain}" for domain in EXTRA_EXACT],
    }
    precise_rules = sorted(set(core_rules) | official_rules())
    full_rules = core_rules + sorted((extra_rules | official_rules()) - set(core_rules))
    core_total = len(core_rules)
    full_total = len(full_rules)

    voice = json.loads(Path("data/chatgpt-voice.json").read_text(encoding="utf-8"))
    voice_rules = []
    for prefix in voice["prefixes"]:
        for family, network in prefix.items():
            if family not in {"ipv4Prefix", "ipv6Prefix"}:
                raise ValueError(f"Unexpected voice prefix field: {family}")
            parsed = ipaddress.ip_network(network)
            kind = "IP-CIDR" if parsed.version == 4 else "IP-CIDR6"
            voice_rules.append(f"{kind},{parsed},no-resolve")
    if not voice_rules:
        raise ValueError("Empty official voice IP list")
    voice_rules = sorted(set(voice_rules))
    voice_header = header + ["# SOURCE: https://openai.com/chatgpt-voice.json",
                             f"# SOURCE-CREATED: {voice['creationTime']}",
                             f"# TOTAL: {len(voice_rules)}"]
    write(Path("rule/Shadowrocket/OpenAI/OpenAI_Voice.list"), voice_header + voice_rules)
    write(Path("rule/Mihomo/OpenAI/OpenAI_Voice.yaml"),
          voice_header + ["payload:"] + [f"  - {rule}" for rule in voice_rules])

    shadow = Path("rule/Shadowrocket/OpenAI")
    write(
        shadow / "OpenAI.list",
        header + [f"# CORE: {core_total}", f"# TOTAL: {full_total}"] + full_rules,
    )
    write(
        shadow / "OpenAI_Core.list",
        header + [f"# TOTAL: {core_total}"] + core_rules,
    )
    write(
        shadow / "OpenAI_Precise.list",
        header + ["# DESCRIPTION: Core plus exact official dependencies; excludes legacy broad provider suffixes.",
                  f"# TOTAL: {len(precise_rules)}"] + precise_rules,
    )
    write(
        shadow / "OpenAI_Keyword.list",
        header + [f"# TOTAL: {len(keywords)}"]
        + [f"DOMAIN-KEYWORD,{keyword}" for keyword in sorted(keywords)],
    )
    write(
        Path("rule/Mihomo/OpenAI/OpenAI_Precise.yaml"),
        header + [f"# TOTAL: {len(precise_rules)}", "payload:"]
        + [f"  - {rule}" for rule in precise_rules],
    )
    write(
        shadow / "OpenAI_Domain.list",
        header
        + [f"# TOTAL: {len(suffixes | exact)}"]
        + [f".{domain}" for domain in sorted(suffixes)]
        + sorted(exact - suffixes),
    )
    write(
        Path("rule/Mihomo/OpenAI/OpenAI.yaml"),
        header
        + [f"# TOTAL: {full_total}", "payload:"]
        + [f"  - {rule}" for rule in full_rules],
    )
    write(
        Path("data/openai-domains.txt"),
        header + [f"# TOTAL: {len(suffixes | exact)}"] + sorted(suffixes | exact),
    )


if __name__ == "__main__":
    main()
