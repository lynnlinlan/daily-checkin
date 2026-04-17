#!/usr/bin/env python3
"""
每日打卡推送脚本 - 由 GitHub Actions 调用
读取 routines.json 生成打卡清单，通过 Server酱/PushPlus 推送到微信
"""

import json
import os
import requests
from datetime import datetime, timezone, timedelta

# 北京时间
CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST)
TODAY = NOW.strftime('%Y-%m-%d')
TODAY_CN = NOW.strftime('%m月%d日')

# 路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINES_FILE = os.path.join(BASE_DIR, 'routines.json')
EXTRAS_FILE = os.path.join(BASE_DIR, 'extras.json')

# 从环境变量读取敏感信息
SERVERCHAN_KEY = os.environ.get('SERVERCHAN_KEY', '')
PUSHPLUS_TOKEN = os.environ.get('PUSHPLUS_TOKEN', '')
PUSH_TYPE = os.environ.get('PUSH_TYPE', 'serverchan')
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY', '')


def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default if default is not None else []


def get_checkin_url():
    """获取打卡页面URL"""
    if GITHUB_REPO:
        return f'https://{GITHUB_REPO.split("/")[0]}.github.io/{GITHUB_REPO.split("/")[1]}/'
    return ''


def build_markdown(routines, extras):
    """生成 Markdown 格式推送内容（Server酱用）"""
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    weekday = weekdays[NOW.weekday()]

    total = len(routines) + len(extras)
    md = f"## 📋 每日打卡 {TODAY_CN} 周{weekday}\n\n"
    md += f"今天共 **{total}** 项待办，点击下方链接开始打卡👇\n\n"

    checkin_url = get_checkin_url()
    if checkin_url:
        md += f'[👉 点击打开打卡页面]({checkin_url})\n'

    return md


def build_html(routines, extras):
    """生成 HTML 格式推送内容（PushPlus用）"""
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    weekday = weekdays[NOW.weekday()]
    total = len(routines) + len(extras)

    checkin_url = get_checkin_url()
    btn = ''
    if checkin_url:
        btn = f'<div style="text-align:center;margin-top:16px;"><a href="{checkin_url}" style="display:inline-block;background:#6366f1;color:#fff;padding:12px 36px;border-radius:8px;text-decoration:none;font-size:16px;font-weight:600;">👉 打开打卡页面</a></div>'

    html = f"""
    <div style="font-family:-apple-system,sans-serif;max-width:480px;margin:0 auto;">
        <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:18px;border-radius:10px;text-align:center;">
            <h2 style="margin:0;font-size:18px;">📋 每日打卡提醒</h2>
            <p style="margin:6px 0 0;opacity:.9;font-size:14px;">{NOW.strftime('%m月%d日')} 周{weekday} · 共{total}项待办</p>
        </div>
        {btn}
    </div>
    """
    return html


def push_serverchan(title, content):
    """通过 Server酱推送（Markdown格式）"""
    if not SERVERCHAN_KEY:
        return {"ok": False, "error": "未设置 SERVERCHAN_KEY 环境变量"}
    resp = requests.post(
        f'https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send',
        json={"title": title, "desp": content},
        timeout=15
    )
    data = resp.json()
    return {"ok": data.get("code") == 0, "data": data}


def push_pushplus(title, content):
    """通过 PushPlus推送（HTML格式）"""
    if not PUSHPLUS_TOKEN:
        return {"ok": False, "error": "未设置 PUSHPLUS_TOKEN 环境变量"}
    resp = requests.post(
        'http://www.pushplus.plus/send',
        json={"token": PUSHPLUS_TOKEN, "title": title, "content": content, "template": "html"},
        timeout=15
    )
    data = resp.json()
    return {"ok": data.get("code") == 200, "data": data}


def main():
    print(f"=== 每日打卡推送 {NOW.isoformat()} ===")

    routines = load_json(ROUTINES_FILE)
    extras = load_json(EXTRAS_FILE, [])

    print(f"常规事项: {[r['name'] for r in routines]}")
    print(f"临时事项: {[e['name'] for e in extras]}")

    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    weekday = weekdays[NOW.weekday()]
    title = f"📋 每日打卡 {TODAY_CN} 周{weekday}"

    if PUSH_TYPE == 'pushplus':
        content = build_html(routines, extras)
        result = push_pushplus(title, content)
    else:
        content = build_markdown(routines, extras)
        result = push_serverchan(title, content)

    if result.get('ok'):
        print("✅ 推送成功！")
    else:
        print(f"❌ 推送失败: {result.get('error', result)}")

    return result


if __name__ == '__main__':
    main()
