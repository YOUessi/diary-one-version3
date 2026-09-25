# Diary One Algorithm V1.74.1｜研究档案字段校正

日期：2026-09-15。状态：**等待本地冻结；算法运行行为相对 V1.74 不变。**

V1.74 首次冻结后的收据复核发现，`codex_d5_research.profile()` 从 V1.73 继承了两项已经失效的说明：

- `stage_models` 仍列出不再调用的 `S09_AHA_SET_EDITOR`；
- `writer_policy_unchanged` 仍宣称 Writer 未改变，并且短编号阶段只列出 S07。

实际 V1.74 运行路径没有调用旧 S09，Writer 也已经使用 V1.74 的请求内短编号；问题仅在研究档案描述，不在算法执行。

V1.74.1 只修改研究档案：

- 删除旧 `S09_AHA_SET_EDITOR` 路由说明；
- 删除 `writer_policy_unchanged`；
- 明确 S07、`S09_AHA_EXPERIENCE_EDITOR` 和 S11 都使用请求内短编号；
- 把 Aha Moment 准确写为“一条事实 + 一张 S04 代表帧”。

未修改 `x02.py`、S04、S07、S09、S10、S11、S12、Prompt、Schema、测试数据、Web/App 默认或模型调用数量。V1.74 首次冻结快照保留且不覆盖；V1.74.1 作为真实素材测试前的说明字段校正版单独冻结。
