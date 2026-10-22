# workbuddy.md — 使用 WorkBuddy 的开发记录

本项目（麦门老黄历 mcd-almanac）**全程在腾讯 WorkBuddy 中开发**。
以下为开发会话的结构化记录，用于核验 WorkBuddy 联动活动奖励条件。

## 开发时间线（2026-10-22）

| 阶段 | 内容 |
|---|---|
| 1. 活动解读 | 拉取大赛官方规则（报名方式、必需文件、排名机制）、RANKING.md 战况、麦当劳 MCP 工具清单（35 个工具） |
| 2. 竞品分析 | 对近 530 份参赛申请做方向研判：省钱/卡路里为红海，「玄学运势」为蓝海 → 定方向「麦门老黄历」 |
| 3. 网页原型 | 赛博黄历单文件 demo（`index.html`）：中文黄历头、8 种状态 chips、转盘开转、运势卡、复制分享、电子木鱼彩蛋 |
| 4. MCP 打通 | initialize / tools/list / tools/call 全链路实测通过；实测发现 `query-nearby-stores` 需 city+keyword 同时传 |
| 5. Skill 实现 | 运势引擎（`YunQiYinQing.py`）+ 零依赖 MCP 客户端（`McpKeHu.py`）+ CLI（`LaoHuangLi.py`）+ 演示数据（`CanPinShuJu.py`）+ 19 项离线自测（`CeShi.py`，全部通过） |
| 6. 真实联调 | 真实 Token 跑通：服务器日期、真实优惠券、160 餐品营养数据、真实门店与可约时段全部挂载成功 |

## 本项目文件与生成方式

- `LaoHuangLi.py` / `YunQiYinQing.py` / `McpKeHu.py` / `CanPinShuJu.py` / `CeShi.py`：由 WorkBuddy 编写，用户环内确认
- `index.html`：由 WorkBuddy 编写（赛博黄历 demo 网页）
- `README.md` / `MCP_INTEGRATION.md` / `SKILL.md`：由 WorkBuddy 编写
- `CONTEST_DECLARATION.md`：官方原版，未做任何修改

## 说明

- 用户可在 WorkBuddy 中导出本会话完整 MD 记录，追加到本文件之后，作为更完整的开发上下文
- ⚠️ **导出前请删除对话中出现的 MCP Token 明文**，遵守参赛声明中「不包含真实 Token、密钥」的信息安全要求
- 本文件记录于 2026-10-22，大赛报名截止 2026-10-25 23:59（北京时间）
