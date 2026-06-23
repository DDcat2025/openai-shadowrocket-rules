from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


EXTRA_EXACT = {
    "browser-intake-datadoghq.com",
    "openai-api.arkoselabs.com",
    "static.cloudflareinsights.com",
}

EXTRA_SUFFIXES = {
    "algolia.net",
    "api.statsig.com",
    "auth0.com",
    "client-api.arkoselabs.com",
    "events.statsigapi.net",
    "featuregates.org",
    "intercom.io",
    "intercomcdn.com",
    "launchdarkly.com",
    "segment.io",
    "sentry.io",
    "statsig.com",
    "statsigapi.net",
    "stripe.com",
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
    full_rules = core_rules + sorted(extra_rules - set(core_rules))
    core_total = len(core_rules)
    full_total = len(full_rules)

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
        shadow / "OpenAI_Domain.list",
        header
        + [f"# TOTAL: {len(suffixes | exact)}"]
        + [f".{domain}" for domain in sorted(suffixes | exact)],
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
