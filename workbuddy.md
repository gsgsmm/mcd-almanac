# workbuddy.md — 使用 WorkBuddy 的开发记录

本项目（麦门老黄历 mcd-almanac）**全程在腾讯 WorkBuddy 中开发**。
以下为开发会话的结构化记录，用于核验作品确实由 WorkBuddy 独立完成。

## 开发时间线（2026-10-22）

| 阶段 | 内容 |
|---|---|
| 1. 大赛规则解读 | 拉取 WorkBuddy「1024 造物挑战」完整活动细则：投稿入口「发布作品」、截止 11-01 23:59、评审维度（创意 35 / 完成度 40 / 体验 25 / 社媒分享 +30）、主题不限 |
| 2. 方向研判 | 对同场作品做方向对比：工具类、题库类、卡牌类扎堆，「玄学运势」为蓝海 → 定方向「麦门老黄历」 |
| 3. 网页原型 | 赛博黄历单文件 demo（`index.html`）：中文黄历头、8 种状态 chips、转盘开转、运势卡、复制签文、电子木鱼彩蛋 |
| 4. MCP 打通 | 麦当劳中国官方 MCP（mcp.mcd.cn）initialize / tools/list / tools/call 全链路实测通过；实测发现 `query-nearby-stores` 需 city+keyword 同时传 |
| 5. Skill 实现 | 运势引擎（`YunQiYinQing.py`）+ 零依赖 MCP 客户端（`McpKeHu.py`）+ CLI（`LaoHuangLi.py`）+ 演示数据（`CanPinShuJu.py`）+ 19 项离线自测（`CeShi.py`，全部通过） |
| 6. 真实联调 | 真实 Token 跑通：服务器日期、真实优惠券、160 餐品营养数据、真实门店与可约时段全部挂载成功 |
| 7. UI 重设计 | 按 UI 专家方案重构为 v2 设计系统：Design Token（宣纸/朱红/墨/金）、字阶与间距体系、十二时辰条、语义色阶运势卡、竖版分享卡、底部拇指操作条、无障碍（aria-live / aria-pressed / 44px 触达 / prefers-reduced-motion） |
| 8. 云服务接入 | 开通 WorkBuddy 云服务，建 `fortune_draws` / `merit_knocks` 两表（RLS 游客模式：公共读 + 游客插入、无 PII、无删改权限），网页接入 SDK：出签与功德实时入库、全站今日签数 / 功德池 / 最新签运 feed |
| 9. 移动端与微信治理 | 320/360/375px 小屏适配实测零横向溢出；补微信 XWeb meta、去除诱导分享敏感词；定位「微信内打不开」根因为平台对 app.workbuddy.host 的统一 UA 引导策略 |
| 10. 缺陷修复 | 真浏览器全链路复验中抓出 `todayKey()` 月份字符串拼接 bug（10 月被算成「91」），修复并清理脏数据；`McpKeHu` 兼容 SSE 响应、券匹配去规格、营养别名去括号 |

## 本项目文件与生成方式

- `LaoHuangLi.py` / `YunQiYinQing.py` / `McpKeHu.py` / `CanPinShuJu.py` / `CeShi.py`：由 WorkBuddy 编写，用户环内确认
- `index.html`：由 WorkBuddy 编写（赛博黄历 demo 网页，v2 设计系统 + 云服务接入 + 移动端适配）
- `README.md` / `MCP_INTEGRATION.md` / `SKILL.md`：由 WorkBuddy 编写
- `CONTEST_DECLARATION.md`：由 WorkBuddy 编写，声明内容为本项目原创性承诺

## 说明

- 用户可在 WorkBuddy 中导出本会话完整 MD 记录，追加到本文件之后，作为更完整的开发上下文
- ⚠️ **导出前请删除对话中出现的 MCP Token 明文**，遵守参赛声明中「不包含真实 Token、密钥」的信息安全要求
- 本文件记录于 2026-10-22，大赛投稿截止 2026-11-01 23:59（北京时间）
