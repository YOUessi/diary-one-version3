# S11–S13 End-to-End Cross-check & User-profile Simulation V1.0

**状态：** PASSED FOR PRODUCTION-SHAPED V1.0 CONTRACT / REAL-DATA CALIBRATION STILL REQUIRED
**日期：** 2026-08-29
**验证对象：** Canonical V1.20–V1.25、closed concept registry、local reference pipeline
**排除：** 真实 VLM/Writer/HQ bytes、App/Firmware、云部署、真实成本/准确率结论

## 1. 检查方法

本轮不是“文档彼此引用就算通过”，而是分四层检查：

1. **合同交叉检查：** S09 membership、V1.20 independence、S10 media、S11 Claim/Tag、S12 validation、S13 activation 是否存在权限冲突。
2. **语义案例模拟：** 用不同用户画像与细时间线检查 Chapter/Aha 的故事职责、文字、索引和失败路径。
3. **结构化失败注入：** 改错 Revision、Claim、Tag、数量、pair、route、Anchor、scope、reuse、D1 等字段，验证能否在正确 stage 被拦截。
4. **可运行证据：** reference fixture 从 S00 handoff 跑到 S13 export，并验证 deterministic rerun、HOLD 不导出和 artifacts 完整性。

## 2. 细时间线案例｜古镇主线＋茶饮店插曲

| 时间 | 可能语义 | S05–S10 结果 | S11–S13 检查 |
|---|---|---|---|
| 09:00 | 古镇入口牌坊 | 古镇 Moment/Beat | Chapter identity 可用，入口可为 Hero |
| 09:02 | 穿过牌坊 | continuity | 可支持“走进/穿过”，需 relation Evidence |
| 09:04 | 石板路近景 | supporting | 只有纹理时不单独形成 Tag/Claim core |
| 09:06 | 两侧传统店面 | architecture Beat candidate | SETTING/ARCHITECTURE 可进入索引 |
| 09:08 | 地图与路牌 | CONTEXT_ONLY 候选 | 可限制地点，不占最终媒体位 |
| 09:10 | 第一座牌坊 | distinct instance candidate | 可作媒体，不必造“牌坊”长期 Tag |
| 09:12 | 同牌坊换角度 | presentation duplicate | 抑制；时间近/远都不能自动 distinct |
| 09:14 | 进入庭院 | spatial progression | Story 可使用“走进庭院”，需顺序证据 |
| 09:16 | 屋檐与斗拱 | aspect candidate | 与外观有独立意义才占 Beat |
| 09:18 | 遮挡严重庭院 | low-quality Evidence | 事实可保留，不能胜任媒体 |
| 09:20 | 大殿外观 | distinct building candidate | 长 Chapter 允许不同建筑外观 |
| 09:22 | 香炉与殿前空间 | support/duplicate test | 非核心时不挤占 3–5 项 |
| 09:24 | 大殿内部 | DUAL_ASPECT | 可与外观共同入选 |
| 09:26 | 木雕细节 | distinct detail Beat | Story 可点木雕，但不必解释“主要画面” |
| 09:28 | 同木雕更近 | replacement | 换更清晰 Anchor，不新增 Beat |
| 09:30 | 路边茶摊 | side detail | 不因出现茶杯给 Chapter FOOD Tag |
| 09:32 | 回到古街 | continuity | 不单独占媒体位 |
| 09:34 | 相似石板路 | duplicate | 时间拉远不自动 distinct |
| 09:36 | 走近石桥 | progression | 可连接街巷→河边 |
| 09:38 | 桥上河道 | river Beat | 可为 Chapter 收束素材 |
| 09:40 | 独立塔楼 | distinct instance | dominant motif 内仍可有不同建筑 |
| 09:42 | 接近塔楼 | supporting progression | 不因距离变化新增 Beat |
| 09:44 | 塔楼正面完整 | strong Anchor/Hero candidate | Title 不必写“塔楼” |
| 09:46 | 人群遮挡塔楼 | poor media | 不否定塔楼 Fact |
| 09:48 | 进入现代茶饮店 | real side episode/break | 不把 A/C 永久 split，也不抹掉 B |
| 09:50 | 点单互动 | support | 不推断关系或满意度 |
| 09:52 | 饮品制作 | support | 外观不能证明“好吃” |
| 09:54 | 猫跳上桌碰倒纸杯 | independent peak candidate | 可成为 embedded-distinct Aha |
| 09:56 | 周围人回应 | adjacent support | 不变成 Aha 第二事件/第二媒体 |
| 09:58 | 离店 | boundary evidence | 证明 side episode 结束 |
| 10:00 | 回到古街 | resumed mainline | Chapter 仍是古镇 citywalk |
| 10:02 | 河边晚光 | closure Beat | Story 可克制收束，需光线 Evidence |

一种合法最终结果：

```text
Chapter Title: 古镇漫步
Chapter Story: 石板路连着旧屋，走到河边时，晚光落在水面。
Chapter Tags: CITY_WALK / HISTORIC_DISTRICT / HISTORIC_ARCHITECTURE / TRAVEL_OUTING
PlaceEntity: 周庄古镇（仅在可信确认时）

Aha Moment Line: 小猫调皮地碰倒了纸杯。
Aha Tags: CAT / CAFE_OR_TEA_SHOP
```

通过条件：猫动作有 Evidence；“调皮”持有窄 light-affect permission；Aha 不依赖 Chapter 才能理解；Chapter 不把猫/纸杯写成自身高潮；Aha 不继承旅行 Tag。

## 3. 十二类用户画像模拟

| ID | 用户/素材 | 预期结果 | 关键风险与检查 | 结果 |
|---|---|---|---|---|
| P01 | 旅行者：三小时古建筑、多个不同建筑 | 1 个长 Chapter，可保留 2–3 个不同外观/方面 | 不把 dominant motif 全去重；也不把同一建筑换角度当 distinct | PASS |
| P02 | 家庭记录者：生日准备、蛋糕、吹蜡烛、合照 | 生日 Chapter 3–5 项；吹蜡烛若为高潮不另作 Aha | same-story redundancy | PASS |
| P03 | 茶饮店猫碰杯插曲 | 古镇 Chapter＋独立宠物 Aha 可共存 | embedded-distinct reservation、单峰、单媒体 | PASS |
| P04 | 手作爱好者：长 Manual 陶艺过程 | 上游已有 distinct units 时可形成过程 Chapter | S13 不偷定 73 秒 Window；“完成”要 outcome Evidence | PASS |
| P05 | 徒步：登山主线＋短暂彩虹 | 徒步 Chapter＋独立彩虹 Aha（证据充分时） | 山顶 outcome 不重复为 Aha | PASS |
| P06 | 普通上班族：通勤、会议、午饭，内容普通 | 0–2 强 Chapter 或 EMPTY_DAY | 不为 3–4 目标凑数，不强塞 Tags | PASS |
| P07 | 稀疏高光：只有清晰求婚 peak | HIGHLIGHT_DAY，exactly 1 Aha | 不补微型 Chapter，不生成 Aha Title/Story | PASS |
| P08 | 美食用户：大量菜品静物，没有反应 | 食物 Chapter 可成立；Aha 通常不成立 | FOOD Tag 不等于“好吃/最爱” | PASS |
| P09 | 宠物用户：猫狗大量重复动作 | presentation 去重；exact pet Entity 可检索 | CAT/DOG class 与豆包/小白实体分离 | PASS |
| P10 | 多次 Sync：上午古镇、晚上聚会 | R2 enrich/retain，R3 新增独立强 Episode | 同义改写抖动、混 Revision、late data | PASS |
| P11 | 用户手改 Chapter Title 后清空 | 非空用户 Title 获显示所有权；清空不自动复活 AI | D2e 最终空 Title presentation deferred | PASS WITH DEFERRED POLICY |
| P12 | 海外用户/英文输出 | locale contract 未 ready 时不机械套中文字符数 | release gate，不影响中文测试 profile | PASS WITH RELEASE GATE |

## 4. Canonical Tag 交叉检查

| Case | 正确索引 | 禁止结果 | 结果 |
|---|---|---|---|
| 周庄古镇 | PlaceEntity + Setting/Activity | 把全球景点写成普通 Concept | PASS |
| 妈妈一起喝咖啡 | verified Person/relation + Activity | 把“妈妈”写进共享 Tag registry | PASS |
| 豆包碰倒纸杯 | PetEntity + CAT + Claim/embedding | 建立 CAT_KNOCK_OVER_CUP 长尾 Tag | PASS |
| 只看到咖啡杯 | FOOD/DRINK subject（若核心） | 自动推断 DRINKING_COFFEE 或 CAFE | PASS |
| 模糊室内 | zero assignment | 长期保存 OTHER_INDOOR | PASS |
| 反复古镇记录 | content frequency | 自动推断“最喜欢古镇” | PASS |
| 中文 label 缺失 | internal assignment 保留、display omitted | 删除 concept 或借英文静默上线 | PASS |

## 5. Narrative 交叉检查

| 文案 | 处理 | 结果 |
|---|---|---|
| `牌坊和木雕构成了上午的主要画面。` | 重写 | 算法选材解释、语气呆板 |
| `石板路连着旧屋，晚光落在水面。` | Evidence 齐全时通过 | 直接呈现场景 |
| `你在最爱的古镇度过了悠闲上午。` | 阻断 | 偏好和内心状态无依据 |
| `小猫调皮地碰倒了纸杯。` | 窄许可通过 | 动作 Claim + CAT subject + light-affect policy |
| `小猫碰倒纸杯，留下难忘一刻。` | 阻断 | “难忘”是用户评价 |
| `随后来到河边。` | 需要 relation | “随后”不能由数组顺序产生 |
| `两座不同古建筑。` | 需要 entity distinctness | 时间远或外观不同不能自动证明“两座” |
| `做完了陶艺作品。` | 需要 process/outcome | 只有拉坯画面不能推完整完成 |

## 6. 三十一类失败注入

| ID | 注入 | 预期 owner/status | 结果 |
|---|---|---|---|
| F01 | S07 artifact 使用 stale Revision | Contract invalid | PASS |
| F02 | S09 selected ID 与 S11 Memory 不一致 | S12 membership invalid | PASS |
| F03 | Chapter/Aha pair decision 缺失 | S12 pair coverage invalid | PASS |
| F04 | CHAPTER_DAY 0 Chapter | S12 Day State invalid | PASS |
| F05 | 2-item Chapter 无 Compact Pair pass | S12 media invalid | PASS |
| F06 | Aha 0/2 visible media | S12 Aha single-media invalid | PASS |
| F07 | Claim 无 Evidence | S11 Claim invalid | PASS |
| F08 | Title/Aha surface 引用不存在 Claim | S11 surface invalid | PASS |
| F09 | Runtime 自由 Tag | S11 unregistered concept | PASS |
| F10 | 同 Facet 分配两个 Concept | S11 facet invalid | PASS |
| F11 | “难忘/最爱”无用户事实 | S11 actual wording invalid | PASS |
| F12 | “调皮”无 exact permission | S11 light-affect invalid | PASS |
| F13 | HQ request 与 RawAsset 不匹配 | S13 contract invalid | PASS |
| F14 | Fallback 改 Anchor/scope | S13 contract invalid | PASS |
| F15 | Primary transient | S13 HOLD，不激活 Fallback | PASS |
| F16 | Primary terminal +合法 Fallback | activation delta + revalidation | PASS |
| F17 | Fallback 产生未声明 cross-Memory reuse | S12B HOLD | PASS |
| F18 | D1 survivor 未预验证/第二次 D1 | HOLD/BLOCK | PASS |
| F19 | D1 删除了 required-media Claim 的唯一依据 | S11 owner replan + S12B HOLD | PASS |
| F20 | canonical memory order 不是 capture chronology | S12 order invalid | PASS |
| F21 | Narrative 缺失 actual-text span binding | S11 contract invalid | PASS |
| F22 | Story 存在没有 Claim/permission 覆盖的文字 | S11 unbound surface text | PASS |
| F23 | span 引用了不在该 surface plan 内的 Claim | S11 unplanned span claim | PASS |
| F24 | 用“调皮”许可包装任意“可爱”等形容词 | S11 tone permission invalid | PASS |
| F25 | Writer model/token/cache/cost provenance 缺失 | S11 envelope invalid | PASS |
| F26 | 两个 Memory 复用同一个 media_id | S11 global identity invalid | PASS |
| F27 | Tag evidence 不属于其引用 Claim | S11 Tag grounding invalid | PASS |
| F28 | Entity evidence 不属于其引用 Claim | S11 Entity grounding invalid | PASS |
| F29 | Aha 正文使用 5 秒 Video | S12 Aha media invalid | PASS |
| F30 | Aha Fallback 切换成 5 秒 Video | S13 route invalid | PASS |
| F31 | 预声明 cross-Memory reuse 实际并非 exact render | S12B HOLD | PASS |

## 7. Local Reference Run Evidence

Reference fixture：`fixtures/production_v1/ancient_town_reference_day.json`。

成功路径实际生成：

```text
S00–S10 CONTRACT_ADAPTER_VALIDATED
S11 PASS
S12A PASS
S13A Primary terminal → same-scope PHOTO Fallback
S12B affected-artifact revalidation PASS
S13B REFERENCE_EXPORT_WRITTEN
full_flow_status = REFERENCE_VALIDATED_NOT_CLOUD_PRODUCTION
```

自动化回归：

```text
72 tests run
71 passed
1 skipped only because local socket test is sandbox-disabled
0 failures
```

覆盖 E00、bundle、evaluator、Evidence Builder、Production V1 与 X01 既有测试；skip 不涉及 V1 full-flow reference。

## 8. Global Invariant Audit

1. False Memory/False Merge 高于 Missing；PASS。
2. RawAsset truth 不被 AI 改写；PASS。
3. Auto 1-or-3/no-refetch 保持；PASS。
4. 任意 Manual 时长未被偷定；PASS。
5. S05 Moment 仍是连续 partition；PASS。
6. A–B–C resumed mainline 不跨 B 合 Moment；PASS。
7. Manual 可去重但事实账本保留；PASS。
8. S09 membership 不被 S10–S13 改变；PASS。
9. Chapter/Aha story independence 保持；PASS。
10. S10 selected-only media/HQ 保持；PASS。
11. S11 每条实际 Claim 可追溯；PASS。
12. Canonical Tag/Entity/Display/Preference 分离；PASS。
13. Provider failure 不变事实/Day State；PASS。
14. S12 不静默修理；PASS。
15. transient 不等于 terminal；PASS。
16. runtime activation immutable；PASS。
17. affected artifacts 重验；PASS。
18. known-invalid prior 不 fallback；PASS。
19. reference 不冒充 cloud Production；PASS。
20. Firmware/SDK/App/shared state 未触碰；PASS。

## 9. 发现并修正的问题

本轮交叉检查产生六项实现/文档修正：

1. 任意 16 秒/73 秒 Manual 曾被 reference code 静默套入 duration buckets；现改为明确 contract error，继续保持 OPEN。
2. 旧 Team Sync 曾允许 S12 现场删除不合法内容；现由 V1.23 收紧为只读 validator＋owner replan。
3. 单次 Fallback pass 不够；现把 affected S11/S12 revalidation 写入实际 runner。
4. S09 canonical order 需要运行时验证；现校验 Chapter/Aha 各自 capture chronology＋stable ID。
5. D1/Hero Alternate 不能只存在文档；现 reference runner 可执行 exact prevalidated one-loss path，并在 Claim 失去依据时 HOLD。
6. Fallback 可能新制造 cross-Memory reuse；现 S12B 对 resulting receipts 再检查必要 reuse decision。

## 10. 结论与限制

S11–S13 产品/算法合同、状态机、失败路由与本地 control-plane reference 在当前范围内交叉一致，没有发现需要重开 S00–S10 的冲突。

尚不能由本检查声称：

- 真实用户素材下 Chapter/Aha precision/recall 已达标；
- VLM/Writer 文字质量、Tag mapping 或 Aha light-affect 已完成校准；
- HQ codec/timebase/source 成功率已验证；
- cohort 月成本目标已由真实 telemetry 证明；
- App、云数据库、对象存储、CAS、隐私/安全已上线。

这些进入 V1.0 后续验证与 Production engineering，不回到“重新想一遍 Pipeline”。
