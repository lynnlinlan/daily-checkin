# 📋 每日打卡 - GitHub Actions 版

每天早上8点自动推送当日打卡清单到微信，同日晚间23:00再次推送已检查当日完成情况 **完全免费，无需服务器**。

## 原理

利用 GitHub Actions 的定时任务（cron），每天自动运行推送脚本，通过 Server酱/PushPlus 推送到微信。

## 一次性设置（5分钟搞定）

### 第1步：Fork 或创建仓库

把本项目推送到你自己的 GitHub 仓库。

### 第2步：配置 Secret

1. 打开你的 GitHub 仓库
2. 点 **Settings** → **Secrets and variables** → **Actions**
3. 点 **New repository secret**，添加：

| Name | Value | 必填 |
|------|-------|------|
| `SERVERCHAN_KEY` | 你的 Server酱 SendKey | 用Server酱时必填 |
| `PUSHPLUS_TOKEN` | 你的 PushPlus Token | 用PushPlus时必填 |

> 两个填一个就行。如果你用 Server酱，就只填 `SERVERCHAN_KEY`。

### 第3步：手动测试一次

1. 打开仓库 → **Actions** 标签页
2. 左侧选 **每日打卡推送**
3. 点 **Run workflow** → **Run workflow**
4. 微信收到消息就说明配通了 ✅

---

## 日常使用

### ✏️ 修改常规事项（增删改）

直接在 GitHub 网页上编辑 `routines.json` 文件：

```json
[
  {
    "name": "吃阿司匹林",
    "category": "health",
    "time": "08:00"
  },
  {
    "name": "复合维生素",
    "category": "health",
    "time": ""
  },
  {
    "name": "鱼油+钙片",
    "category": "health",
    "time": "08:00"
  }
]
```

- **加一项**：在数组里加一个 `{"name": "xxx", "category": "health", "time": "08:00"}`
- **删一项**：删掉对应的那行
- **改名**：直接改 `name` 的值

改完 Commit 保存，第二天推送就自动生效。

### 📝 添加临时事项

编辑 `extras.json`：

```json
[
  { "name": "下午3点开会", "done": false },
  { "name": "取快递", "done": false }
]
```

### 🕐 修改推送时间

编辑 `.github/workflows/daily-push.yml` 里的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'   # UTC时间，对照表↓
```

| 想在北京时间 | 填UTC |
|-------------|-------|
| 7:00 | `23 * * *` |
| 8:00 | `0 0 * * *` |
| 9:00 | `1 0 * * *` |

### 分类说明

| category | 显示 |
|----------|------|
| health | 💊 健康 |
| life | 🏠 生活 |
| work | 💼 工作 |
| other | 📌 其他 |

## 文件说明

```
├── .github/workflows/
│   └── daily-push.yml    # GitHub Actions 定时任务配置
├── push.py               # 推送脚本
├── routines.json         # 常规事项（每天重复）
├── extras.json           # 临时事项（手动编辑）
└── config.json           # 配置
```
