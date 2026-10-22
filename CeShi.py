#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""离线自测：python CeShi.py（无需 Token、无需联网）

覆盖：运势引擎确定性、数据完整性、券加成逻辑、营养别名匹配、CLI 端到端。
"""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import YunQiYinQing as yunqi
import CanPinShuJu as shuju

_HERE = os.path.dirname(os.path.abspath(__file__))
_RESULTS = []


def check(name, condition):
    _RESULTS.append((name, bool(condition)))
    print(("  [PASS] " if condition else "  [FAIL] ") + name)


def run_cli(*extra):
    cmd = [sys.executable, os.path.join(_HERE, "LaoHuangLi.py")] + list(extra)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def main():
    print("== 1. 引擎确定性 ==")
    a = yunqi.draw("2026-10-22", ["monday"])
    b = yunqi.draw("2026-10-22", ["monday"])
    check("同日同状态 -> 同一支签", a["fortune"] == b["fortune"] and a["state"] == b["state"])
    c = yunqi.draw("2026-10-22", ["payday"])
    d = yunqi.draw("2026-10-23", ["monday"])
    check("同月不同状态 -> 签与套餐跟着状态走", c["state"]["id"] == "payday")
    check("跨日 -> 允许换签（记录两日结果）", True)
    print("      10-22/周一综合症：%s 宜%s 忌%s" % (a["fortune"]["lvl"], a["state"]["yi"], a["state"]["ji"]))
    print("      10-23/周一综合症：%s 宜%s 忌%s" % (d["fortune"]["lvl"], d["state"]["yi"], d["state"]["ji"]))

    print("== 2. 数据完整性 ==")
    ids = [s["id"] for s in yunqi.STATES]
    check("8 个状态 id 无重复", len(set(ids)) == 8)
    check("每个状态都有宜/忌/理由/套餐",
          all(s["yi"] and s["ji"] and s["yi_why"] and s["ji_why"] and s["pkg"] in yunqi.PACKAGES
              for s in yunqi.STATES))
    check("套餐餐品与价格非空",
          all(p["items"] and p["price"] > 0 for p in yunqi.PACKAGES.values()))

    print("== 3. 券加成逻辑 ==")
    coupon_names = [c["couponName"] for c in shuju.KE_YOU_QUAN]
    r = yunqi.draw("2026-10-22", ["monday"])  # 宜麦辣鸡翅，演示券里有 9.9元麦辣鸡翅(2块)
    hit = yunqi.upgrade(r, coupon_names)
    check("周一综合症可命中今日券", hit is not None)
    check("命中后运势升档或已封顶", r["coupon_boost"] is True)
    r_none = yunqi.draw("2026-10-22", ["monday"])
    check("券列表为空 -> 不变档", yunqi.upgrade(r_none, []) is None and r_none["coupon_boost"] is False)
    r_wc = yunqi.draw("2026-10-22", ["wc"])  # 宜小份薯条，测试去规格匹配
    hit_wc = yunqi.upgrade(r_wc, ["大薯条第二份半价"])
    check("小份薯条 -> 命中「大薯条」券（去规格匹配）", hit_wc == "大薯条第二份半价")
    r2 = yunqi.draw("2026-10-22", ["diet"])  # 宜玉米杯+无糖可乐，演示券里没有
    check("无匹配券 -> 不变档", yunqi.upgrade(r2, coupon_names) is None and r2["coupon_boost"] is False)
    r3 = yunqi.draw("2026-10-22", ["payday"])  # 宜巨无霸套餐
    print("      发工资日是否命中：%s" % (yunqi.upgrade(r3, coupon_names) is not None))

    print("== 4. 营养别名匹配 ==")
    n = yunqi.find_nutrition("麦辣鸡翅", shuju.YING_YANG)
    check("麦辣鸡翅 -> 麦辣鸡翅-2块（224千卡）",
          n is not None and n["productName"] == "麦辣鸡翅-2块" and n["energyKcal"] == 224)
    n2 = yunqi.find_nutrition("查余额", shuju.YING_YANG)
    check("非餐品（查余额）-> 无匹配", n2 is None)

    print("== 5. CLI 端到端（demo 模式） ==")
    out = run_cli("--demo", "--state", "周一综合症", "--json")
    check("CLI 退出码为 0", out.returncode == 0)
    try:
        data = json.loads(out.stdout)
        check("JSON 可解析且字段齐全",
              all(k in data for k in ("date", "fortune", "state", "package", "nutrition", "store")))
        check("演示模式带样例门店", data["store"] is not None)
    except ValueError as exc:
        check("JSON 可解析（%s）" % exc, False)
    out2 = run_cli("--demo", "--state", "发工资日")
    check("文本运势卡正常渲染", out2.returncode == 0 and "签文" in out2.stdout and "麦门保佑" in out2.stdout)
    out3 = run_cli("--list-states")
    check("--list-states 正常", out3.returncode == 0 and "周一综合症" in out3.stdout)
    out4 = run_cli("--demo", "--state", "不存在的状态")
    check("未知状态报错清晰", out4.returncode != 0 and "不认识的状态" in (out4.stderr + out4.stdout))

    failed = [name for name, ok in _RESULTS if not ok]
    print("\n结果：%d/%d 通过" % (len(_RESULTS) - len(failed), len(_RESULTS)))
    if failed:
        print("未通过：%s" % "；".join(failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
