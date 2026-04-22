# 🌅 KieDex BOT

> Automated airdrop farming with multi-account and proxy support

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/vonssy/Kiedex-BOT.svg)](https://github.com/vonssy/Kiedex-BOT/stargazers)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Setup & Usage](#setup--usage)
- [Proxy Recommendation](#proxy-recommendation)
- [Support](#support)
- [Contributing](#contributing)

## 🎯 Overview

KieDex BOT is an automated tool designed to airdrop farming across multiple accounts. It provides seamless offers robust proxy support for enhanced security and reliability performance.

**🔗 Get Started:** [Register on KieDex](https://kiedex.app?ref=QZ08LUX3)

> **Important:** signup with google and connect new evm wallet

## ✨ Features

- 🔄 **Automated Account Management** - Retrieve account information automatically
- 🌐 **Flexible Proxy Support** - Run with or without proxy configuration
- 🔀 **Smart Proxy Rotation** - Automatic rotation of invalid proxies
- 🚰 **Daily Faucet** - Automated claim daily USDT faucet
- ⛽ **Daily Bonus** - Automated claim daily OIL
- 📝 **Complete Tasks** - Automated complete available tasks
- 📈 **Open Position** - Automated trade in BTC/USDT
- 👥 **Multi-Account Support** - Manage multiple accounts simultaneously

## 📋 Requirements

- **Python:** Version 3.9 or higher
- **pip:** Latest version recommended

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vonssy/Kiedex-BOT.git
cd Kiedex-BOT
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
# or for Python 3 specifically
pip3 install -r requirements.txt
```

## ⚙️ Configuration

### Account Configuration

<div align="center">
  <img src="images/example.png" alt="KieDex Tokens Example" width="500">
  <p><em>Example of fetching kiedex tokens</em></p>
</div>

Create or edit `accounts.josn` in the project directory:

```json
[
    {
        "email": "your_email_address_1",
        "access_token": "access_token",
        "refresh_token": "refresh_token"
    },
    {
        "email": "your_email_address_2",
        "access_token": "access_token",
        "refresh_token": "refresh_token"
    }
]
```

### Proxy Configuration (Optional)

Create or edit `proxy.txt` in the project directory:

```
# Simple format (HTTP protocol by default)
192.168.1.1:8080

# With protocol specification
http://192.168.1.1:8080
https://192.168.1.1:8080

# With authentication
http://username:password@192.168.1.1:8080
```

### Start the Bot

After running the setup, launch the KieDex BOT:

```bash
python bot.py
# or for Python 3 specifically
python3 bot.py
```

### Runtime Options

When starting the bot, you'll be prompted to choose:

1. **Proxy Mode Selection:**
   - Option `1`: Run with proxy
   - Option `2`: Run without proxy

2. **Auto-Rotation:** 
   - `y`: Enable automatic invalid proxy rotation
   - `n`: Disable auto-rotation

## 💖 Support the Project

If this project has been helpful to you, consider supporting its development:

### Cryptocurrency Donations

| Network | Address |
|---------|---------|
| **EVM** | `0xe3c9ef9a39e9eb0582e5b147026cae524338521a` |
| **TON** | `UQBEFv58DC4FUrGqinBB5PAQS7TzXSm5c1Fn6nkiet8kmehB` |
| **SOL** | `E1xkaJYmAFEj28NPHKhjbf7GcvfdjKdvXju8d8AeSunf` |
| **SUI** | `0xa03726ecbbe00b31df6a61d7a59d02a7eedc39fe269532ceab97852a04cf3347` |

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

1. ⭐ **Star this repository** if you find it useful
2. 👥 **Follow** for updates on new features
3. 🐛 **Report issues** via GitHub Issues
4. 💡 **Suggest improvements** or new features
5. 🔧 **Submit pull requests** for bug fixes or enhancements

## 📞 Contact & Support

- **Developer:** vonssy
- **Issues:** [GitHub Issues](https://github.com/vonssy/Kiedex-BOT/issues)
- **Discussions:** [GitHub Discussions](https://github.com/vonssy/Kiedex-BOT/discussions)

---

<div align="center">

**Made with ❤️ by [vonssy](https://github.com/vonssy)**

*Thank you for using Kiedex Validator BOT! Don't forget to ⭐ star this repository.*

</div>