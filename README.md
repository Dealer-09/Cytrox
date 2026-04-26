# 🛡️ RepoShield: Zero-Trust Git Protection

**RepoShield** is a modern, high-performance CLI tool designed to protect developers from malicious repositories. It intercepts `git clone` commands and reroutes them through an isolated, containerized security sandbox before they ever touch your host machine.

![Gradient Banner](https://img.shields.io/badge/Aesthetic-Immersive_CLI-cyan)
![Security](https://img.shields.io/badge/Security-Zero--Trust-purple)
![Docker](https://img.shields.io/badge/Backend-Docker_Sandbox-blue)

## ✨ Features

- **🛡️ Secure Sandbox**: Uses Docker to build a temporary, isolated Ubuntu environment to scan code.
- **🔍 Triple-Threat Scanning**: Executes **Semgrep**, **Bandit**, and **Gitleaks** to detect SAST vulnerabilities, Python-specific issues, and hardcoded secrets.
- **🌈 Immersive UI**: Features a character-by-character gradient banner and modern CLI decorators.
- **📊 Detailed Reporting**:
  - **Terminal Tables**: Instant breakdown of findings by Severity, Category, and Description.
  - **Monotone HTML Report**: Clean, professional security audit dashboards that auto-open in your browser.
  - **JSON Export**: Raw data for integration into other security tools.
- **⚙️ Customizable Policies**:
  - **Strict Mode**: Automatically block malicious clones.
  - **Filtering**: Ignore specific severities or tool categories via `reposhield configure`.

---

## 🚀 Getting Started

### Installation

1. Ensure **Docker Desktop** is running.
2. Download the `reposhield.exe` from the latest release.
3. Open a terminal (PowerShell recommended) and run:
   ```powershell
   .\reposhield.exe install
   ```
4. Restart your terminal.

### Usage

Once installed, RepoShield automatically protects you whenever you clone:

```powershell
git clone https://github.com/vulnerable/repo
```

Or call it directly:

```powershell
reposhield clone <repo_url>
```

To tweak your security threshold:

```powershell
reposhield configure
```

---

## 🛠️ Technology Stack

- **CLI Engine**: [Typer](https://typer.tiangolo.com/) (Python)
- **UI Framework**: [Rich](https://github.com/Textualize/rich)
- **Containerization**: [Docker SDK for Python](https://docker-py.readthedocs.io/)
- **Scanning Tools**: Semgrep, Bandit, Gitleaks

---

## 🔐 Zero-Trust Philosophy
RepoShield treats every remote repository as potentially compromised. By requiring a successful sandbox scan before writing any data to your disk, it eliminates the risk of "clone-to-pwn" attacks and accidental secret leakage.

---
*Built with ❤️ for a safer open-source ecosystem.*