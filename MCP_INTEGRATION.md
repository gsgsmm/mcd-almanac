# MCP 集成说明（MCP_INTEGRATION.md）

## MCP Server

- **服务**：麦当劳中国官方 MCP Server（mcd-mcp）
- **接入地址**：`https://mcp.mcd.cn`（Streamable HTTP）
- **协议版本**：2025-03-26
- **认证方式**：请求头 `Authorization: Bearer <MCD_MCP_TOKEN>`
- **Token 申请**：https://open.mcd.cn/mcp （手机号登录 → 控制台 → 激活）
- **本项目用法**：Token 仅通过环境变量 `MCD_MCP_TOKEN` 或本地 `.env`（已被 .gitignore 忽略）注入，**不写入任何代码与提交文件**

## 使用的工具

| 工具 | 用途 | 使用模式 |
|---|---|---|
| `now-time-info` | 获取服务器真实日期，作为「麦历」的日期源 | 真实模式 |
| `available-coupons` | 拉取今日可领优惠券，参与「有券升档」运势加成 | 真实模式 |
| `list-nutrition-foods` | 160 个餐品官方营养数据，为宜/忌及套餐餐品挂热量与蛋白质 | 真实模式 |
| `query-nearby-stores` | 按城市+关键词查附近门店、营业时间、可预约时段 | 真实模式（需 `--city` + `--keyword`） |
| `query-meals` / `calculate-price` / `create-order` | 门店级菜单、真实算价与下单 | 未接入（见「降级策略」） |

## 调用流程

```
initialize 握手 → notifications/initialized
        │
        ▼
now-time-info ──────────► 今日日期（麦历日期源）
        │
        ▼
本地运势引擎抽签 ◄────── 宜/忌/签文/开运套餐（YunQiYinQing.py）
        │
        ▼
available-coupons ──────► 命中「宜」的事项 → 运势升一档（封顶大吉）
        │
        ▼
list-nutrition-foods ───► 为宜/忌与套餐餐品补充 热量/蛋白质
        │
        ▼
query-nearby-stores ────► 展示「开运门店」与今日可约时段（可选）
        │
        ▼
输出运势卡（文本 / --json）
```

## 业务价值

1. **把「今天吃什么」这个每日高频决策娱乐化**：老黄历的「宜/忌」格式零学习成本，签文与吐槽理由提供情绪价值，天然适合社交分享。
2. **真实数据让玄学「讲道理」**：运势不是纯随机——每日真实优惠券会改变结果，餐品建议附带官方营养数据，娱乐外壳 + 数据内核。
3. **零门槛体验**：`--demo` 模式无需 Token 全离线可跑，降低试用成本；`--json` 输出方便网页/机器人二次集成。

## 降级策略

- **无 Token**：自动进入演示模式，使用与真实返回结构一致的样例数据（`CanPinShuJu.py`）
- **单工具失败**（网络/限流/参数）：仅跳过对应数据 enrichment，主流程继续，并在输出 `notes` 中如实标注
- **门店查询参数**：实测 `query-nearby-stores` 在 `searchType=2` 时 `city` 与 `keyword` **必须同时传入**，否则返回「城市名或者关键词不能为空」

## 安全与合规

- Token 仅经环境变量 / 本地 `.env` 注入，仓库内不含任何真实 Token、密钥（符合参赛声明信息安全要求）
- 本项目**不调用 `create-order`**：只出建议不代付，支付由用户自行确认
- 项目输出仅供参考，餐品与价格信息以麦当劳官方渠道实时结果为准
