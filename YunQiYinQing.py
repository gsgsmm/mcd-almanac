# -*- coding: utf-8 -*-
"""麦门老黄历 · 运势引擎

纯本地规则引擎，零第三方依赖：
把「今日状态」翻译成 宜 / 忌 / 签文 / 开运套餐。

仪式感设计：同一个「日期 + 状态」组合永远抽到同一支签——
今日一签，明日复位，黄历的脾气就是这么倔。
"""

import hashlib
import random

# ============ 今日状态 ============
# yi / ji：宜与忌的事项；yi_why / ji_why：吐槽式理由；pkg：对应开运套餐
STATES = [
    {"id": "monday", "label": "周一综合症",
     "yi": "麦辣鸡翅", "yi_why": "以辣解忧，辣醒昏迷的周一",
     "ji": "白开水", "ji_why": "越喝越淡，周一忌淡",
     "pkg": "monday"},
    {"id": "wc", "label": "带薪如厕",
     "yi": "小份薯条", "yi_why": "悄无声息，体面摸鱼",
     "ji": "麦辣鸡腿堡", "ji_why": "香味太冲，容易暴露",
     "pkg": "wc"},
    {"id": "lieflat", "label": "周末躺平",
     "yi": "麦乐送全家桶", "yi_why": "床以外的地方都是远方",
     "ji": "出门堂食", "ji_why": "躺平人，今天不出门",
     "pkg": "lieflat"},
    {"id": "diet", "label": "减肥第三天",
     "yi": "玉米杯+无糖可乐", "yi_why": "低卡续命，心理安慰拉满",
     "ji": "巧克力甜筒", "ji_why": "第三天的意志，经不起试探",
     "pkg": "diet"},
    {"id": "breakup", "label": "失恋第7天",
     "yi": "双层吉士堡", "yi_why": "双倍芝士，填补空心",
     "ji": "双人套餐", "ji_why": "前任的座位，先空着",
     "pkg": "breakup"},
    {"id": "overtime", "label": "加班夜归人",
     "yi": "24h热咖啡", "yi_why": "深夜续命，麦门收留",
     "ji": "空腹入睡", "ji_why": "胃里空空，心里更空",
     "pkg": "overtime"},
    {"id": "payday", "label": "发工资日",
     "yi": "巨无霸套餐", "yi_why": "赚钱不花，过期作废",
     "ji": "查余额", "ji_why": "快乐经不起对账",
     "pkg": "payday"},
    {"id": "exam", "label": "考前突击",
     "yi": "麦满分早餐", "yi_why": "一顿满分，科科满分",
     "ji": "甜筒", "ji_why": "化得太快，知识点也是",
     "pkg": "exam"},
]

STATE_MAP = {s["id"]: s for s in STATES}

# ============ 吉凶与签文 ============
FORTUNES = [
    {"lvl": "大吉", "tag": "麦门庇佑 · 诸事皆宜", "poem": "麦门庇佑，薯条镇楼，横财就手"},
    {"lvl": "中吉", "tag": "运势回甘 · 宜趁热打铁", "poem": "可乐去冰，烦恼清零，万事可期"},
    {"lvl": "小吉", "tag": "小确幸 · 稳住别慌", "poem": "甜筒压惊，明日再战，稳住别慌"},
    {"lvl": "半吉", "tag": "喜忧参半 · 心态要平", "poem": "麦辣开胃，运势回甘，先吃再说"},
    {"lvl": "平", "tag": "平平淡淡 · 养生局", "poem": "玉米杯养生，苟住就是胜利"},
    {"lvl": "凶", "tag": "大凶 · 但有解法", "poem": "今日大凶，宜呼友共食，可破"},
]

# ============ 开运套餐（演示价格，接入门店级算价后替换） ============
PACKAGES = {
    "monday": {"name": "周一清醒包", "items": [["麦辣鸡腿堡", 18.5], ["小份薯条", 7.0], ["可口可乐(中)", 7.5]], "price": 33.0},
    "wc": {"name": "摸鱼安静包", "items": [["小份薯条", 7.0], ["无糖可乐(中)", 7.5], ["玉米杯", 6.5]], "price": 21.0},
    "lieflat": {"name": "躺平全家桶", "items": [["麦乐送全家桶", 64.0], ["圆筒冰淇淋", 6.0], ["可口可乐(中)", 7.5]], "price": 77.5},
    "diet": {"name": "减脂安慰餐", "items": [["玉米杯", 6.5], ["无糖可乐(中)", 7.5], ["苹果片", 6.0]], "price": 20.0},
    "breakup": {"name": "疗愈双倍包", "items": [["双层吉士堡", 15.5], ["麦乐鸡(5块)", 12.0], ["可口可乐(中)", 7.5]], "price": 35.0},
    "overtime": {"name": "深夜疗愈包", "items": [["鲜萃咖啡(大杯)", 13.0], ["麦乐鸡(5块)", 12.0]], "price": 25.0},
    "payday": {"name": "发工资狂欢包", "items": [["巨无霸", 21.5], ["麦辣鸡翅(2块)", 13.0], ["圆筒冰淇淋", 6.0]], "price": 40.5},
    "exam": {"name": "满分冲刺包", "items": [["猪柳蛋麦满分", 15.0], ["鲜萃咖啡(大杯)", 13.0], ["脆薯饼", 6.0]], "price": 34.0},
}

# ============ 营养数据别名 ============
# 运势里的餐品名 -> 麦当劳官方营养表（list-nutrition-foods）里的标准名
YING_YANG_ALIAS = {
    "麦辣鸡翅": "麦辣鸡翅-2块",
    "小份薯条": "小薯条",
    "麦辣鸡腿堡": "麦辣鸡腿汉堡",
    "圆筒冰淇淋": "圆筒冰淇淋",
    "巧克力甜筒": "圆筒冰淇淋",
    "甜筒": "圆筒冰淇淋",
    "玉米杯": "大杯玉米杯",
    "无糖可乐": "无糖可口可乐中杯",
    "苹果片": "苹果片",
    "麦乐鸡": "麦乐鸡5块",
    "双层吉士堡": "双层吉士汉堡",
    "巨无霸套餐": "巨无霸",
    "巨无霸": "巨无霸",
    "24h热咖啡": "大杯鲜萃咖啡",
    "热咖啡": "大杯鲜萃咖啡",
    "麦满分早餐": "猪柳蛋麦满分",
    "麦满分": "猪柳蛋麦满分",
    "脆薯饼": "脆薯饼",
    "可乐": "可乐中杯",
    "可口可乐": "可乐中杯",
}


def _seed_of(*parts):
    """把任意参数组合成一个稳定的整数种子。"""
    raw = "|".join(str(p) for p in parts)
    return int(hashlib.md5(raw.encode("utf-8")).hexdigest()[:8], 16)


def draw(date_str, state_ids):
    """抽今日签。

    date_str: 'YYYY-MM-DD'；state_ids: 状态 id 列表（可为空）。
    同一组合永远得到同一结果——这就是「今日一签，明日复位」。
    """
    ids = sorted(set(state_ids)) if state_ids else []
    rng = random.Random(_seed_of(date_str, ",".join(ids)))
    fortune = FORTUNES[rng.randrange(len(FORTUNES))]
    if ids:
        state = STATE_MAP[ids[rng.randrange(len(ids))]]
    else:
        state = STATES[rng.randrange(len(STATES))]
    return {
        "date": date_str,
        "fortune": dict(fortune),
        "state": dict(state),
        "package": PACKAGES[state["pkg"]],
        "coupon_boost": False,
        "coupon_hit": None,
    }


def upgrade(result, coupon_names):
    """今日有券加成：如果「宜」的事项今天能领到券，运势升一档（封顶大吉）。

    返回命中的券名（未命中返回 None）。这是「黄历每天不一样」的真实数据来源。
    """
    hit = match_coupon(result["state"]["yi"], coupon_names)
    if not hit:
        return None
    order = [f["lvl"] for f in FORTUNES]  # 索引 0 = 大吉 …… 5 = 凶
    current = order.index(result["fortune"]["lvl"])
    if current > 0:
        result["fortune"] = dict(FORTUNES[current - 1])
    result["coupon_boost"] = True
    result["coupon_hit"] = hit
    return hit


def match_coupon(item_name, coupon_names):
    """餐品名今天有没有券可领。返回券名或 None。

    匹配规则：全名 + 去掉规格词（小/中/大/迷你/份）与场景词（套餐/早餐）的核心名，
    例如「小份薯条」也能命中写「薯条」的券。
    """
    if not item_name or not coupon_names:
        return None
    keys = set()
    for base in [item_name, YING_YANG_ALIAS.get(item_name)]:
        if not base:
            continue
        for part in base.replace("+", " ").split():
            keys.add(part)
            core = part.split("-")[0].split("(")[0]
            for prefix in ("小份", "中份", "大份", "迷你", "小", "中", "大"):
                if core.startswith(prefix) and len(core) > len(prefix):
                    core = core[len(prefix):]
            for suffix in ("套餐", "早餐"):
                if core.endswith(suffix) and len(core) > len(suffix):
                    core = core[:-len(suffix)]
            keys.add(core)
    for coupon in coupon_names:
        for key in keys:
            if len(key) >= 2 and key in coupon:
                return coupon
    return None


def find_nutrition(item_name, nutrition_list):
    """在官方营养数据里查餐品，返回 dict 或 None。

    全名查不到时，会去掉括号规格再试一次：「可口可乐(中)」->「可口可乐」。
    """
    if not item_name or not nutrition_list:
        return None
    target = YING_YANG_ALIAS.get(item_name)
    if not target and "(" in item_name:
        target = YING_YANG_ALIAS.get(item_name.split("(")[0])
    if not target:
        return None
    for item in nutrition_list:
        if isinstance(item, dict) and item.get("productName") == target:
            return item
    return None
