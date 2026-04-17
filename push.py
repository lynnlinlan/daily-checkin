#!/usr/bin/env python3
"""
每日打卡推送脚本 - 由 GitHub Actions 调用
读取 routines.json 生成打卡清单，通过 Server酱/PushPlus 推送到微信
"""

import json
import os
import requests
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
NOW = datetime.now(CST)
TODAY = NOW.strftime('%Y-%m-%d')
TODAY_CN = NOW.strftime('%m月%d日')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINES_FILE = os.path.join(BASE_DIR, 'routines.json')

SERVERCHAN_KEY = os.environ.get('SERVERCHAN_KEY', '')
PUSHPLUS_TOKEN = os.environ.get('PUSHPLUS_TOKEN', '')
PUSH_TYPE = os.environ.get('PUSH_TYPE', 'serverchan')


def load_routines():
    with open(ROUTINES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_message(routines):
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    weekday = weekdays[NOW.weekday()]
    title = f"📋 每日打卡 {TODAY_CN} 周{weekday}"

    html = f"""
    <div style="font-family:-apple-system,sans-serif;max-width:480px;margin:0 auto;">
        <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;padding:18px;border-radius:10px;text-align:center;margin-bottom:12px;">
            <h2 style="margin:0;font-size:18px;">📋 每日打卡提醒</h2>
            <p style="margin:4px 0 0;opacity:.85;font-size:13px;">{NOW.strftime('%Y年%m月%d日')} 周{weekday}</p>
        </div>
    """

    if routines:
        html += '<div style="background:#f0f7ff;border-radius:8px;padding:10px 12px;margin-bottom:10px;">'
        html += '<h3 style="margin:0 0 6px;color:#1a73e8;font-size:14px;">🔄 常规事项</h3>'
        for r in routines:
            cat = r.get('category', '')
            cat_map = {'health': '💊', 'life': '🏠', 'work': '💼', 'other': '📌'}
            cat_icon = cat_map.get(cat, '📌')
            time_str = f' <span style="color:#db2777;font-size:12px;">⏰{r["time"]}</span>' if r.get('time') else ''
            html += f'<div style="padding:3px 0;font-size:14px;">⬜ {cat_icon} {r["name"]}{time_str}</div>'
        html += '</div>'

    html += """
        <div style="background:#fef7e0;border-radius:8px;padding:10px 12px;margin-bottom:10px;">
            <h3 style="margin:0 0 6px;color:#e37400;font-size:14px;">📝 临时事项</h3>
            <div style="font-size:13px;color:#999;">今天有临时待办？编辑仓库 extras.json 添加</div>
        </div>
        <div style="text-align:center;color:#999;font-size:12px;margin-top:8px;">
            💪 坚持就是胜利！打卡完记得去打勾～
        </div>
    </div>
    """
    return title, html


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
    print(f"=== 每日打卡推送 {NOW.isoformat()} ===")
    routines = load_routines()
    print(f"常规事项: {[r['name'] for r in routines]}")
    title, content = build_message(routines)

    if PUSH_TYPE == 'pushplus':
        result = push_pushplus(title, content)
    else:
        result = push_serverchan(title, content)

    if result.get('ok'):
        print("✅ 推送成功！")
    else:
        print(f"❌ 推送失败: {result.get('error', result)}")
    return result


if __name__ == '__main__':
    main()
