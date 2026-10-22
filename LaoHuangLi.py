#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""麦门老黄历 · 命令行入口

用法示例：
    python LaoHuangLi.py --list-states                    # 看看有哪些今日状态
    python LaoHuangLi.py --state 周一综合症                # 有 Token 自动走真实 MCP 数据
    python LaoHuangLi.py --state 周一综合症 --demo         # 强制演示模式（离线可跑）
    python LaoHuangLi.py --state 发工资日,周末躺平 --json   # 多状态 + 机器可读输出
    python LaoHuangLi.py --state 加班夜归人 --city 上海 --keyword 麦当劳   # 附真实门店

Token 配置（三选一，都不写进代码）：
    1. 环境变量：set MCD_MCP_TOKEN=xxx（Windows） / export MCD_MCP_TOKEN=xxx
    2. 本地 .env 文件：MCD_MCP_TOKEN=xxx（已被 .gitignore 忽略，不会进仓库）
    3. 不配置：自动进入 --demo 演示模式
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import YunQiYinQing as yunqi
from McpKeHu import McpKeHu
import CanPinShuJu as shuju

BAN_BEN = "1.0.0"
CN_NUM = ["〇", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
CN_MONTH = ["", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]


# ---------- 工具函数 ----------
def load_env():
    """加载脚本同目录的 .env（仅本地，已被 .gitignore 忽略）。"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def pick_mode(args):
    """决定真实模式还是演示模式，返回 (client_or_None, 模式说明)。"""
    load_env()
    token = os.environ.get("MCD_MCP_TOKEN", "").strip()
    if args.demo or not token:
        return None, "演示模式（未配置 MCP Token，使用离线数据）"
    return McpKeHu(token), "真实模式（麦当劳中国官方 MCP · mcp.mcd.cn）"


def safe_call(client, tool, arguments, fallback, notes):
    """带降级的工具调用：失败不炸主流程，只在 notes 里记账。"""
    try:
        return client.call_tool(tool, arguments)
    except Exception as exc:  # 网络/限流/参数问题一律降级
        notes.append("%s 调用失败，已降级：%s" % (tool, exc))
        return fallback


def as_list(value):
    """把 MCP 返回统一成 list。"""
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return value.get("data") or value.get("list") or []
    return []


def resolve_states(names):
    """把 --state 传入的中文名/id 解析成状态 id 列表。"""
    by_id = {s["id"]: s for s in yunqi.STATES}
    by_label = {s["label"]: s for s in yunqi.STATES}
    ids = []
    for raw in names:
        for piece in str(raw).replace("，", ",").split(","):
            piece = piece.strip()
            if not piece:
                continue
            if piece in by_id:
                ids.append(piece)
            elif piece in by_label:
                ids.append(by_label[piece]["id"])
            else:
                raise SystemExit("不认识的状态：「%s」，用 --list-states 看看有哪些" % piece)
    return ids


def cn_date(date_str):
    """'2026-10-22' -> '麦历二〇二六年 · 十月廿二'。"""
    try:
        year, month, day = (int(x) for x in date_str.split("-"))
    except ValueError:
        return date_str
    year_cn = "".join(CN_NUM[int(c)] for c in str(year))
    if day == 10:
        day_cn = "初十"
    elif day == 20:
        day_cn = "二十"
    elif day == 30:
        day_cn = "三十"
    else:
        tens, ones = divmod(day, 10)
        tens_cn = {1: "十", 2: "廿"}.get(tens, CN_NUM[tens] + "十")
        day_cn = tens_cn + (CN_NUM[ones] if ones else "")
    return "麦历%s年 · %s月%s" % (year_cn, CN_MONTH[month], day_cn)


# ---------- 运势卡渲染 ----------
def render(payload):
    state = payload["state"]
    fortune = payload["fortune"]
    package = payload["package"]
    nutrition = payload["nutrition"]
    store = payload.get("store")
    lines = []
    lines.append("━" * 34)
    lines.append("   🪔 麦门老黄历 · mcd-almanac v%s" % BAN_BEN)
    lines.append("   " + cn_date(payload["date"]))
    lines.append("━" * 34)
    lines.append("  【%s】%s" % (fortune["lvl"], fortune["tag"]))
    if payload.get("coupon_boost"):
        lines.append("  ⚡ 今日有券加成：%s（运势升档）" % payload["coupon_hit"])
    lines.append("  " + "─" * 32)
    lines.append("  宜  %s" % state["yi"])
    lines.append("       %s" % state["yi_why"])
    if nutrition.get("yi"):
        n = nutrition["yi"]
        lines.append("       🥗 %s · %s千卡 · 蛋白质%sg" % (n.get("productName", ""), n.get("energyKcal", "?"), n.get("protein", "?")))
    lines.append("  忌  %s" % state["ji"])
    lines.append("       %s" % state["ji_why"])
    if nutrition.get("ji"):
        n = nutrition["ji"]
        lines.append("       🥗 %s · %s千卡" % (n.get("productName", ""), n.get("energyKcal", "?")))
    lines.append("  " + "─" * 32)
    lines.append("  签文：「%s」" % fortune["poem"])
    lines.append("  " + "─" * 32)
    lines.append("  开运套餐 · %s" % package["name"])
    for entry in nutrition.get("package", []):
        nut = entry.get("nutrition")
        suffix = ""
        if nut:
            suffix = "（%s千卡）" % nut.get("energyKcal", "?")
        lines.append("    · %-14s ¥%-6.1f%s" % (entry.get("name", ""), entry.get("price", 0), suffix))
    lines.append("  参考价 ¥%.1f（演示价格，非官方报价）" % package["price"])
    if store:
        lines.append("  " + "─" * 32)
        lines.append("  开运门店 · %s" % store.get("storeName", ""))
        lines.append("    %s · %s-%s" % (store.get("address", ""),
                                        store.get("businessStartTime", "?"),
                                        store.get("businessEndTime", "?")))
        options = store.get("reservationTimeOptions") or []
        for option in options:
            if option.get("today"):
                lines.append("    今日可约：%s" % option.get("reservationOptionText", ""))
                break
    lines.append("  " + "─" * 32)
    lines.append("  数据：%s" % payload["mode"])
    for note in payload.get("notes", []):
        lines.append("  备注：%s" % note)
    lines.append("  提醒：本工具只建议不代付，下单支付请自行确认")
    lines.append("  麦门保佑 🫐")
    return "\n".join(lines)


# ---------- 主流程 ----------
def main():
    parser = argparse.ArgumentParser(
        prog="麦门老黄历",
        description="今天宜吃什么？让黄历决定。麦当劳 MCP 驱动的赛博玄学点餐 Skill。")
    parser.add_argument("--state", action="append", default=[],
                        help="今日状态，可多次或逗号分隔，如：周一综合症,发工资日")
    parser.add_argument("--city", default=None, help="城市（查真实门店时必填，需与 --keyword 一起传）")
    parser.add_argument("--keyword", default=None, help="位置关键词（查真实门店时必填）")
    parser.add_argument("--demo", action="store_true", help="强制演示模式（离线可跑）")
    parser.add_argument("--json", action="store_true", dest="as_json", help="以 JSON 输出")
    parser.add_argument("--list-states", action="store_true", help="列出所有今日状态")
    parser.add_argument("--version", action="version", version="mcd-almanac v%s" % BAN_BEN)
    args = parser.parse_args()

    if args.list_states:
        print("今日状态（--state 可传一个或多个，中文名或 id 都行）：")
        for state in yunqi.STATES:
            print("  %-10s %s" % (state["id"], state["label"]))
        return

    client, mode_note = pick_mode(args)
    notes = []

    # 1) 今日日期（真实模式取服务器时间，麦历的日期源）
    if client:
        time_info = safe_call(client, "now-time-info", {}, shuju.SHI_JIAN, notes)
    else:
        time_info = shuju.SHI_JIAN
    date_str = time_info.get("date") if isinstance(time_info, dict) else None
    if not date_str:
        date_str = datetime.date.today().isoformat()

    # 2) 抽签
    state_ids = resolve_states(args.state)
    result = yunqi.draw(date_str, state_ids)

    # 3) 今日可领优惠券（有券升档——黄历每日不同的真实数据来源）
    if client:
        coupons_raw = safe_call(client, "available-coupons", {}, shuju.KE_YOU_QUAN, notes)
    else:
        coupons_raw = shuju.KE_YOU_QUAN
    coupon_names = [c.get("couponName", "") for c in as_list(coupons_raw)]
    coupon_hit = yunqi.upgrade(result, coupon_names)

    # 4) 官方营养数据（为宜/忌与套餐餐品挂真实热量蛋白质）
    if client:
        nutrition_list = safe_call(client, "list-nutrition-foods", {}, shuju.YING_YANG, notes)
    else:
        nutrition_list = shuju.YING_YANG
    nutrition_list = as_list(nutrition_list) or shuju.YING_YANG
    yi_nutrition = yunqi.find_nutrition(result["state"]["yi"], nutrition_list)
    ji_nutrition = yunqi.find_nutrition(result["state"]["ji"], nutrition_list)
    pkg_nutrition = [(name, price, yunqi.find_nutrition(name, nutrition_list))
                     for name, price in result["package"]["items"]]

    # 5) 附近门店（真实模式需 --city + --keyword；演示模式给样例门店）
    store = None
    if client and args.city and args.keyword:
        stores = safe_call(client, "query-nearby-stores",
                           {"beType": 1, "searchType": 2, "city": args.city, "keyword": args.keyword},
                           [], notes)
        stores = as_list(stores)
        if stores:
            store = stores[0]
    elif not client:
        store = shuju.MEN_DIAN[0]

    payload = {
        "project": "麦门老黄历 mcd-almanac",
        "version": BAN_BEN,
        "mode": mode_note,
        "date": date_str,
        "fortune": result["fortune"],
        "state": result["state"],
        "package": result["package"],
        "coupon_boost": result["coupon_boost"],
        "coupon_hit": coupon_hit,
        "coupons_today": coupon_names,
        "nutrition": {
            "yi": yi_nutrition,
            "ji": ji_nutrition,
            "package": [
                {"name": name, "price": price,
                 "nutrition": ({"productName": nut.get("productName"),
                                "energyKcal": nut.get("energyKcal"),
                                "protein": nut.get("protein")} if nut else None)}
                for name, price, nut in pkg_nutrition
            ],
        },
        "store": store,
        "notes": notes,
    }

    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render(payload))


if __name__ == "__main__":
    main()
