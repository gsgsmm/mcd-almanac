# -*- coding: utf-8 -*-
"""演示数据：没有 MCP Token 时的离线替代数据（--demo 模式）。

结构与麦当劳 MCP 的真实返回保持一致，方便无痕体验与离线自测。
"""

# 服务器时间（now-time-info 的返回结构）
SHI_JIAN = {
    "date": "2026-10-22",
    "formatted": "2026-10-22 12:00:00",
    "dayOfWeek": "THURSDAY",
}

# 今日可领优惠券（available-coupons 的返回结构）
KE_YOU_QUAN = [
    {"couponName": "11.9元麦辣鸡腿堡", "couponStatus": "CAN_GET", "label": "可领取"},
    {"couponName": "19.9元王牌炸鸡任选2", "couponStatus": "CAN_GET", "label": "可领取"},
    {"couponName": "免费脆薯饼", "couponStatus": "CAN_GET", "label": "可领取"},
    {"couponName": "9.9元麦辣鸡翅(2块)", "couponStatus": "CAN_GET", "label": "可领取"},
]

# 官方营养数据子集（list-nutrition-foods 的返回结构，字段与真实接口一致）
YING_YANG = [
    {"productName": "麦辣鸡腿汉堡", "energyKcal": 485, "protein": 24, "fat": 24, "carbohydrate": 42, "sodium": 1208},
    {"productName": "麦辣鸡翅-2块", "energyKcal": 224, "protein": 13, "fat": 15, "carbohydrate": 9, "sodium": 537},
    {"productName": "小薯条", "energyKcal": 210, "protein": 3, "fat": 9, "carbohydrate": 28, "sodium": 120},
    {"productName": "中薯条", "energyKcal": 289, "protein": 4, "fat": 12, "carbohydrate": 38, "sodium": 165},
    {"productName": "圆筒冰淇淋", "energyKcal": 93, "protein": 2, "fat": 3, "carbohydrate": 14, "sodium": 36},
    {"productName": "麦乐鸡5块", "energyKcal": 213, "protein": 12, "fat": 12, "carbohydrate": 13, "sodium": 422},
    {"productName": "大杯玉米杯", "energyKcal": 87, "protein": 4, "fat": 1, "carbohydrate": 12, "sodium": 2},
    {"productName": "小杯玉米杯", "energyKcal": 53, "protein": 2, "fat": 1, "carbohydrate": 7, "sodium": 1},
    {"productName": "无糖可口可乐中杯", "energyKcal": 0, "protein": 0, "fat": 0, "carbohydrate": 1, "sodium": 35},
    {"productName": "可乐中杯", "energyKcal": 147, "protein": 0, "fat": 0, "carbohydrate": 36, "sodium": 0},
    {"productName": "苹果片", "energyKcal": 32, "protein": 0, "fat": 0, "carbohydrate": 7, "sodium": 0},
    {"productName": "双层吉士汉堡", "energyKcal": 429, "protein": 27, "fat": 22, "carbohydrate": 31, "sodium": 1017},
    {"productName": "巨无霸", "energyKcal": 513, "protein": 27, "fat": 26, "carbohydrate": 42, "sodium": 961},
    {"productName": "猪柳蛋麦满分", "energyKcal": 387, "protein": 23, "fat": 21, "carbohydrate": 25, "sodium": 846},
    {"productName": "大杯鲜萃咖啡", "energyKcal": 13, "protein": 1, "fat": 0, "carbohydrate": 0, "sodium": 3},
    {"productName": "脆薯饼", "energyKcal": 146, "protein": 1, "fat": 9, "carbohydrate": 14, "sodium": 311},
]

# 附近门店（query-nearby-stores 的返回结构）
MEN_DIAN = [
    {
        "storeCode": "1450104",
        "storeName": "麦当劳上海黄浦悦荟广场餐厅",
        "address": "南京东路３５３号（山东中路九江路）",
        "businessStartTime": "06:30",
        "businessEndTime": "23:59",
        "reservation": True,
        "reservationTimeOptions": [
            {"date": "2026-10-22", "today": True,
             "reservationOptionText": "午餐(10:44至14:15)，下午茶(14:44至16:45)，夜市(17:14至21:45)，宵夜(22:14至23:45)"},
        ],
    }
]
