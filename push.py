#!/usr/bin/env python3
"""
每日打卡推送脚本 - 由 GitHub Actions 调用
PUSH_MODE: morning=早上提醒, evening=晚上检查
"""

import json
import os
import requests
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST)
TODAY_CN = NOW.strftime('%m月%d日')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINES_FILE = os.path.join(BASE_DIR, 'routines.json')
EXTRAS_FILE = os.path.join(BASE_DIR, 'extras.json')

SERVERCHAN_KEY = os.environ.get('SERVERCHAN_KEY', '')
PUSHPLUS_TOKEN = os.environ.get('PUSHPLUS_TOKEN', '')
PUSH_TYPE = os.environ.get('PUSH_TYPE', 'serverchan')
PUSH_MODE = os.environ.get('PUSH_MODE', 'morning')
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY', '')


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
    md = f"## 🌅 早安！打卡提醒\n\n"
    md += f"今天共 **{total}** 项待办\n\n"
    url = get_checkin_url()
    if url:
        md += f'[👉 点击打开打卡页面]({url})\n'
    return md


def build_evening_md(routines, extras):
    total = len(routines) + len(extras)
    md = f"## 🌙 今日打卡检查\n\n"
    md += f"共 **{total}** 项待办，别忘了补打卡！\n\n"
    url = get_checkin_url()
    if url:
        md += f'[👉 点击打开打卡页面]({url})\n'
    return md


def build_morning_html(routines, extras):
    total = len(routines) + len(extras)
    url = get_checkin_url()
    btn = ''
    if url:
        btn = f'<div style="text-align:center;margin-top:16px;"><a href="{url}" style="display:inline-block;background:#6366f1;color:#fff;padding:12px 36px;border-radius:8px;text-decoration:none;font-size:16px;font-weight:600;">👉 打开打卡页面</a></div>'
    return f"""
    <div style="font-family:-apple-system,sans-serif;max-width:480px;margin:0 auto;">
        <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:18px;border-radius:10px;text-align:center;">
            <h2 style="margin:0;font-size:18px;">🌅 早安！打卡提醒</h2>
            <p style="margin:6px 0 0;opacity:.9;font-size:14px;">今天共{total}项待办</p>
        </div>
        {btn}
    </div>
    """


def build_evening_html(routines, extras):
    total = len(routines) + len(extras)
    url = get_checkin_url()
    btn = ''
    if url:
        btn = f'<div style="text-align:center;margin-top:16px;"><a href="{url}" style="display:inline-block;background:#f59e0b;color:#fff;padding:12px 36px;border-radius:8px;text-decoration:none;font-size:16px;font-weight:600;">👉 打开打卡页面</a></div>'
    return f"""
    <div style="font-family:-apple-system,sans-serif;max-width:480px;margin:0 auto;">
        <div style="background:linear-gradient(135deg,#1e3a5f 0%,#2d5a87 100%);color:#fff;padding:18px;border-radius:10px;text-align:center;">
            <h2 style="margin:0;font-size:18px;">🌙 今日打卡检查</h2>
            <p style="margin:6px 0 0;opacity:.9;font-size:14px;">共{total}项待办，别忘了补打卡！</p>
        </div>
        {btn}
    </div>
    """


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
    is_evening = PUSH_MODE == 'evening'
    mode_label = "晚间检查" if is_evening else "早间提醒"
    print(f"=== 每日打卡推送 ({mode_label}) {NOW.isoformat()} ===")

    routines = load_json(ROUTINES_FILE)
    extras = load_json(EXTRAS_FILE, [])
    total = len(routines) + len(extras)

    print(f"共 {total} 项待办")

    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    weekday = weekdays[NOW.weekday()]

    if is_evening:
        title = f"🌙 打卡检查 {TODAY_CN} 周{weekday}"
    else:
        title = f"🌅 打卡提醒 {TODAY_CN} 周{weekday}"

    if PUSH_TYPE == 'pushplus':
        content = build_evening_html(routines, extras) if is_evening else build_morning_html(routines, extras)
        result = push_pushplus(title, content)
    else:
        content = build_evening_md(routines, extras) if is_evening else build_morning_md(routines, extras)
        result = push_serverchan(title, content)

    if result.get('ok'):
        print("✅ 推送成功！")
    else:
        print(f"❌ 推送失败: {result.get('error', result)}")
    return result


if __name__ == '__main__':
    main()
