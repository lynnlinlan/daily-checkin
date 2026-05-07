#!/usr/bin/env python3
"""
每日打卡推送脚本 - 由 GitHub Actions 调用
自带时间判断：只在指定时间窗口内推送，其他时间跳过
"""

import json
import os
import requests
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST)
HOUR = NOW.hour
TODAY_CN = NOW.strftime('%m月%d日')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINES_FILE = os.path.join(BASE_DIR, 'routines.json')
EXTRAS_FILE = os.path.join(BASE_DIR, 'extras.json')

SERVERCHAN_KEY = os.environ.get('SERVERCHAN_KEY', '')
PUSHPLUS_TOKEN = os.environ.get('PUSHPLUS_TOKEN', '')
PUSH_TYPE = os.environ.get('PUSH_TYPE', 'serverchan')
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY', '')

# 推送时间窗口（北京时间小时数）
MORNING_WINDOW = [8, 9]
EVENING_WINDOW = [22, 23]


def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default if default is not None else []


def get_checkin_url():
    if GITHUB_REPO:
        return f'https://{GITHUB_REPO.split("/")[0]}.github.io/{GITHUB_REPO.split("/")[1]}/'
    return ''


def build_morning_md(routines, extras):
    total = len(routines) + len(extras)
    md = f"## 🌅 早安！打卡提醒\n\n今天共 **{total}** 项待办\n\n"
    url = get_checkin_url()
    if url:
        md += f'[👉 点击打开打卡页面]({url})\n'
    return md


def build_evening_md(routines, extras):
    total = len(routines) + len(extras)
    md = f"## 🌙 今日打卡检查\n\n共 **{total}** 项待办，别忘了补打卡！\n\n"
    url = get_checkin_url()
    if url:
        md += f'[👉 点击打开打卡页面]({url})\n'
    return md


def push_serverchan(title, content):
    if not SERVERCHAN_KEY:
        return {"ok": False, "error": "未设置 SERVERCHAN_KEY"}
    resp = requests.post(
        f'https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send',
        json={"title": title, "desp": content}, timeout=15
    )
    data = resp.json()
    return {"ok": data.get("code") == 0, "data": data}


def push_pushplus(title, content):
    if not PUSHPLUS_TOKEN:
        return {"ok": False, "error": "未设置 PUSHPLUS_TOKEN"}
    resp = requests.post(
        'http://www.pushplus.plus/send',
        json={"token": PUSHPLUS_TOKEN, "title": title, "content": content, "template": "html"},
        timeout=15
    )
    data = resp.json()
    return {"ok": data.get("code") == 200, "data": data}


def main():
    print(f"=== 当前北京时间: {NOW.strftime('%Y-%m-%d %H:%M')} ===")

    if HOUR in MORNING_WINDOW:
        push_mode = 'morning'
    elif HOUR in EVENING_WINDOW:
        push_mode = 'evening'
    else:
        print(f"当前小时 {HOUR} 不在推送窗口内，跳过")
        print(f"早间窗口: {MORNING_WINDOW}, 晚间窗口: {EVENING_WINDOW}")
        return

    is_evening = push_mode == 'evening'
    mode_label = "晚间检查" if is_evening else "早间提醒"
    print(f"→ 执行{mode_label}推送")

    routines = load_json(ROUTINES_FILE)
    extras = load_json(EXTRAS_FILE, [])
    total = len(routines) + len(extras)
    print(f"共 {total} 项待办")

    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    weekday = weekdays[NOW.weekday()]

    if is_evening:
        title = f"🌙 打卡检查 {TODAY_CN} 周{weekday}"
        content = build_evening_md(routines, extras)
    else:
        title = f"🌅 打卡提醒 {TODAY_CN} 周{weekday}"
        content = build_morning_md(routines, extras)

    if PUSH_TYPE == 'pushplus':
        result = push_pushplus(title, content)
    else:
        result = push_serverchan(title, content)

    if result.get('ok'):
        print("✅ 推送成功！")
    else:
        print(f"❌ 推送失败: {result.get('error', result)}")


if __name__ == '__main__':
    main()
