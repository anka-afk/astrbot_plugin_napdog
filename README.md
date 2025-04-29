# 🐾 AstrBot NapDog Cleaner

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/Python-3.10.14%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen)](CONTRIBUTING.md)
[![Contributors](https://img.shields.io/github/contributors/anka-afk/astrbot_plugin_napdog?color=green)](https://github.com/anka-afk/astrbot_plugin_napdog/graphs/contributors)
[![Last Commit](https://img.shields.io/github/last-commit/anka-afk/astrbot_plugin_napdog)](https://github.com/anka-afk/astrbot_plugin_napdog/commits/main)

</div>

<div align="center">

[![Moe Counter](https://count.getloli.com/get/@NapDogCleaner?theme=moebooru)](https://github.com/anka-afk/astrbot_plugin_napdog)

</div>

NapDog Cleaner - 自动监控并清理 NapCat 产生的缓存文件，防止磁盘空间被占满！

## ✨ 功能特性

- 🔄 自动定期监控 NapCat 缓存目录大小
- 🧹 当缓存超过阈值时自动清理
- 🐳 支持 Docker 环境和普通环境自动适配
- 🛡️ 防止缓存文件占用过多磁盘空间
- ⚙️ 可自定义清理阈值和时间间隔

## 🛠️ 配置说明

### 基本配置

在插件配置中设置以下参数:

```json
{
  "clean_size": {
    "description": "缓存大小阈值(MB)",
    "type": "int",
    "hint": "当缓存大小超过此值时触发清理，默认100MB",
    "default": 100
  },
  "cleanup_interval": {
    "description": "清理检查间隔(秒)",
    "type": "int",
    "hint": "多久检查一次缓存大小，建议3600-7200秒",
    "default": 3600
  },
  "napcat_cache_dir": {
    "description": "缓存目录路径",
    "type": "string",
    "hint": "留空则根据环境自动选择",
    "default": ""
  }
}
```

### 🐳 Docker 环境配置

在 Docker 环境中使用时，需要确保 NapCat 的缓存目录能够被 NapDog 插件访问到。推荐以下配置方式：

#### 方式一：共享卷挂载

```yaml
# docker-compose.yml
services:
  napcat:
    # NapCat 服务配置
    volumes:
      - napcat-cache:/root/.config/QQ/NapCat/temp

  astrbot:
    # AstrBot 服务配置
    volumes:
      - napcat-cache:/napcat-cache # 挂载相同卷到不同路径
    environment:
      - PLUGIN_NAPDOG_NAPCAT_CACHE_DIR=/napcat-cache

volumes:
  napcat-cache:
```

#### 方式二：直接挂载宿主机目录

```yaml
# docker-compose.yml
services:
  napcat:
    # NapCat 服务配置
    volumes:
      - ./data/napcat-cache:/root/.config/QQ/NapCat/temp

  astrbot:
    # AstrBot 服务配置
    volumes:
      - ./data/napcat-cache:/napcat-cache
    environment:
      - PLUGIN_NAPDOG_NAPCAT_CACHE_DIR=/napcat-cache
```

## 🔄 版本历史

- v1.0.0
  - ✅ 实现基础的缓存监控与清理功能
  - ✅ 支持 Docker 环境自动检测
  - ✅ 自定义清理阈值和时间间隔

## 👥 贡献指南

欢迎通过以下方式参与项目：

- 🐛 提交 Issue 报告问题
- 💡 提出新功能建议
- 🔧 提交 Pull Request 改进代码

## 🌟 鸣谢

感谢所有为这个项目做出贡献的开发者！

---

> 让你的系统始终保持整洁，NapDog 会默默守护 🐕
