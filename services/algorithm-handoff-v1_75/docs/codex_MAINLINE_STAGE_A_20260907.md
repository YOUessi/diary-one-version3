# Codex 主干优化 A｜真实评价基线与下一步

日期：2026-09-07。状态：本地准备完成；算法仍是 V1.68，没有新模型运行、质量通过或接入变更。

## 本步做完了什么

将已归档的真实问题与正向结果整理成六个可定位的评价案例，逐项保留卡片、候选、事实和全部相关抽帧。不是新增六条运行规则，不是六份独立用户样本，也没有将我的评价当成你的评分。

当前源码/合同与 V1.68 清单的 43 个摘要一致；包 1、2 完整结果及实际结构请求的摘要已复核。包 3 没有 V1.68 模型结果，不借用 V1.67 冒充同版本基线。保留现有用户工作区与独立 App R2，不覆盖旧检查点。

机器可读定位表：[真实案例基线](<ORIGINAL_REPOSITORY/var/codex_mainline_stage_a_20260907/codex_real_case_baseline.json>)。该表属于本地研究材料，包含素材事实和路径，不默认公开发布，也不作为下一次模型输入里的示例答案。

## 新确认的完整路径

素材包 2 的 16、17、18、19、20.jpg 均已进入结构调用，且均为 KEEP（可参与候选），没有因为解码或字数丢失而缺席。事实文字分别记录餐食桌面、夜间餐车和街边小吃；16、17 的事实本身并未明确写“室内”，室内判断还依靠真实图片及场景提示。因此不能预先断言纯事实文字一定比带提示更充分。

- 结构模型先将 **16、17、19、20** 合成饮食 Chapter，漏掉餐车远景 **18**。
- 后续精选保留 **16、17、19**，未展示街边小吃 **20**。
- 因此最终是两张室内餐食加一张夜间餐车。混组源头在结构环节，不是 Writer 临时把好组写坏了。
- 结构模型自己的解释已区分茶店/餐厅与夜市，却仍用宽泛饮食主题连接它们；这证明它并非完全未察觉场景差异，但不证明原事实足以还原所有实际关系。
- 20 的事实支持为 STRONG，质量自评 0.85，但事件分类为 NONE/NONE，未进入既有 Aha 候选资格。能否成为好 Aha 尚待用户评价，不能直接写成“必须选出”。

辅助标签与事实也并不总一致：18 被标为街道/步行，19 被标为市场/饮食；两张文字却都提到夜间路边餐车。16、17 的场景标签是茶店，但事实主要讲用餐桌面。这提供了一个可对照的假设：**辅助分类和预分组是否压过了真实事实之间的联系？** 目前没有实验结果证明该假设。

## 六个评价案例

只评价指定维度。正向案例不代表整张卡的文字、时序和全部属性都被认可；修复也不要求复刻原始标题、成员名单或唯一切分。

### R01｜室内用餐与夜市被宽泛饮食主题误合

范围：素材包 2，S07。性质：真实结果缺陷。

结构候选包含16、17、19、20；最终精选是16、17、19。18在结构输入中有事实且为KEEP，但没有进入该组。夜市18/19/20是值得评估的子组，不保证18的画质或三者的连接已达到最终发布标准。

检查目标：不能仅因同属饮食合章；每个成员需要具体连接证据。允许不成章，不强制某个标题或固定分组答案。

原始卡片（不改写）：

- **烟火里的食光**；卡片 ID：`59537c03-0e8a-5790-b76a-c361ccb8de6f`；候选 ID：`48a09770-fa37-5189-8566-9ea91be780da`。
  > 铜锅热气腾腾，烤盘上肉块与腌黄瓜相映；夜市餐车亮灯待客，蓝橙车身旁三名顾客驻足，一桌一摊皆是人间烟火。

相关素材（“全部抽帧”用于避免以单张预览代替完整证据）：

- [16.jpg](<OWNER_CONTROLLED_TEST_PACK_2/16.jpg>)；最终展示于：烟火里的食光；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_2/round_1/evidence/asset_d71b2488-fcc5-4302-8fff-4cacaa3defb4/frame_w00_4500.jpg>)。
- [17.jpg](<OWNER_CONTROLLED_TEST_PACK_2/17.jpg>)；最终展示于：烟火里的食光；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_2/round_1/evidence/asset_1d37813a-2a14-435c-837a-8bf217eb233e/frame_w00_4500.jpg>)。
- [19.jpg](<OWNER_CONTROLLED_TEST_PACK_2/19.jpg>)；最终展示于：烟火里的食光；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_2/round_1/evidence/asset_369e17df-827c-4c04-831b-bf23a1a152f2/frame_w00_4500.jpg>)。
- [20.jpg](<OWNER_CONTROLLED_TEST_PACK_2/20.jpg>)；未在本案例卡片中展示；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_2/round_1/evidence/asset_5111fc58-d949-4d13-8d11-359f7fadd4dc/frame_w00_4500.jpg>)。
- [18.jpg](<OWNER_CONTROLLED_TEST_PACK_2/18.jpg>)；未在本案例卡片中展示；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_2/round_1/evidence/asset_3b306637-f504-4569-89df-150820deb56d/frame_w00_4500.jpg>)。

你的评价：〔待填〕。可以直接反馈“R01，哪一个素材应移出/保留，以及原因”。

### R02｜不同对象可以共同支持林径经历

范围：素材包 1，S07。性质：应保护的已有正向能力。

继承V1.68已归档完整四帧审阅：祈福牌素材还包含林木、水边、石桥与台阶，不能只用第一张牌子图片判无关。本例只认可成员可连接，不认可全部时序措辞或重复Aha。

检查目标：不能因对象不同机械拆掉有证据连接的经历；也不要求原分组一字不变。

原始卡片（不改写）：

- **林径步移**；卡片 ID：`82bfc3c3-e7eb-5961-ae72-dac0d6758f3c`；候选 ID：`250522b7-1e78-562f-b7b2-ed6bcbe5bee9`。
  > 青石小径蜿蜒入林，棕白狗背影随落叶起伏，苔痕斑驳的石阶与树影低垂，静默铺展成一方呼吸的节奏。

相关素材（“全部抽帧”用于避免以单张预览代替完整证据）：

- [09ed75eff07f6aac0133ab3e542c4b3d.mp4](<OWNER_CONTROLLED_TEST_PACK_1/09ed75eff07f6aac0133ab3e542c4b3d.mp4>)；最终展示于：林径步移；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w00_7500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w01_1500.jpg>) · [帧 4](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w01_7500.jpg>)。
- [6576b04fcedee8130e6c9d1650be78e0.mp4](<OWNER_CONTROLLED_TEST_PACK_1/6576b04fcedee8130e6c9d1650be78e0.mp4>)；最终展示于：林径步移；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_6522750f-ce02-4ede-8a12-a195e05012ee/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_6522750f-ce02-4ede-8a12-a195e05012ee/frame_w00_4500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_6522750f-ce02-4ede-8a12-a195e05012ee/frame_w00_7500.jpg>)。
- [c9a75a21437b5d5462cf39a8c0cbba28.mp4](<OWNER_CONTROLLED_TEST_PACK_1/c9a75a21437b5d5462cf39a8c0cbba28.mp4>)；最终展示于：林径步移；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w00_7500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w01_1500.jpg>) · [帧 4](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w01_7500.jpg>)。

你的评价：〔待填〕。可以直接反馈“R02，哪一个素材应移出/保留，以及原因”。

### R03｜古巷不同画面具有共同探索内容

范围：素材包 1，S07。性质：应保护的已有正向能力。

继承V1.68已归档图像审阅的正向组织结果；七个候选成员精选为三个。不是所有古建筑必须同章，也不是所有候选都必须保留。

检查目标：修复宽泛误合时，不能把有支持的跨对象探索全部拆碎；只评价事实支持与清晰度，不锁定原标题或唯一答案。

原始卡片（不改写）：

- **古巷拾遗**；卡片 ID：`3824e166-4f18-5c3a-9389-b35b6f260187`；候选 ID：`63b15f2c-6075-50e6-b015-eadc02e32f1b`。
  > 石阶、红灯笼与'禹贡古村'牌坊次第展开，'古越龍山'石刻在湿润台阶旁悄然落定，历史在脚下无声延展。

相关素材（“全部抽帧”用于避免以单张预览代替完整证据）：

- [250b1bad4d5d8da24c53ebe4151bb7ab.mp4](<OWNER_CONTROLLED_TEST_PACK_1/250b1bad4d5d8da24c53ebe4151bb7ab.mp4>)；最终展示于：古巷拾遗；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_82575557-6628-4715-82e5-73f3f761fcc4/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_82575557-6628-4715-82e5-73f3f761fcc4/frame_w00_7500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_82575557-6628-4715-82e5-73f3f761fcc4/frame_w01_1500.jpg>) · [帧 4](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_82575557-6628-4715-82e5-73f3f761fcc4/frame_w01_7500.jpg>)。
- [522e4d072f337def753aed8c7a94ed1c.mp4](<OWNER_CONTROLLED_TEST_PACK_1/522e4d072f337def753aed8c7a94ed1c.mp4>)；最终展示于：古巷拾遗；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_e59c9bd4-d59f-433f-87d5-1e11ed9ad1dd/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_e59c9bd4-d59f-433f-87d5-1e11ed9ad1dd/frame_w00_7500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_e59c9bd4-d59f-433f-87d5-1e11ed9ad1dd/frame_w01_1500.jpg>) · [帧 4](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_e59c9bd4-d59f-433f-87d5-1e11ed9ad1dd/frame_w01_7500.jpg>)。
- [7452dabf532b1523cd6603b58dc17122.mp4](<OWNER_CONTROLLED_TEST_PACK_1/7452dabf532b1523cd6603b58dc17122.mp4>)；未在本案例卡片中展示；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_bec8a5dd-76b0-4c98-8019-818e3d403378/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_bec8a5dd-76b0-4c98-8019-818e3d403378/frame_w00_4500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_bec8a5dd-76b0-4c98-8019-818e3d403378/frame_w00_7500.jpg>)。
- [8a1e021316c7825618fc85ba70d5da7c.mp4](<OWNER_CONTROLLED_TEST_PACK_1/8a1e021316c7825618fc85ba70d5da7c.mp4>)；未在本案例卡片中展示；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_dba5ff94-dbad-47a5-82c8-fdc040ea1b6c/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_dba5ff94-dbad-47a5-82c8-fdc040ea1b6c/frame_w00_4500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_dba5ff94-dbad-47a5-82c8-fdc040ea1b6c/frame_w00_7500.jpg>)。
- [b719cb94a859f6662df605abfc7b0b43.mp4](<OWNER_CONTROLLED_TEST_PACK_1/b719cb94a859f6662df605abfc7b0b43.mp4>)；最终展示于：古巷拾遗；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_b4731ca8-3d6c-4cb3-81cd-32fd1fa43774/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_b4731ca8-3d6c-4cb3-81cd-32fd1fa43774/frame_w00_4500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_b4731ca8-3d6c-4cb3-81cd-32fd1fa43774/frame_w00_7500.jpg>)。
- [d0d0dc192e11c9a244b79518023ffa1e.mp4](<OWNER_CONTROLLED_TEST_PACK_1/d0d0dc192e11c9a244b79518023ffa1e.mp4>)；未在本案例卡片中展示；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_8122576f-bfde-4917-814a-b2ac71e3fd08/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_8122576f-bfde-4917-814a-b2ac71e3fd08/frame_w00_7500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_8122576f-bfde-4917-814a-b2ac71e3fd08/frame_w01_1500.jpg>) · [帧 4](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_8122576f-bfde-4917-814a-b2ac71e3fd08/frame_w01_7500.jpg>)。
- [f5840e15a65526b128c68a22385a5247.mp4](<OWNER_CONTROLLED_TEST_PACK_1/f5840e15a65526b128c68a22385a5247.mp4>)；未在本案例卡片中展示；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_ffe80baa-fa51-4bab-8ca1-e1fbfb87ed8c/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_ffe80baa-fa51-4bab-8ca1-e1fbfb87ed8c/frame_w00_7500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_ffe80baa-fa51-4bab-8ca1-e1fbfb87ed8c/frame_w01_1500.jpg>) · [帧 4](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_ffe80baa-fa51-4bab-8ca1-e1fbfb87ed8c/frame_w01_7500.jpg>)。

你的评价：〔待填〕。可以直接反馈“R03，哪一个素材应移出/保留，以及原因”。

### R04｜同一林径小狗故事被Chapter与Aha重复发布

范围：素材包 1，EDITORIAL_ALLOCATION。性质：真实结果缺陷。

同一source asset成为Chapter核心表达与Aha；当前缺失的关系以UNRESOLVED共存。本例不据此推导必须删除Aha或必须删除Chapter。

检查目标：应明确两张卡是否提供独立记忆价值；如果同故事不应双发。最终哪种形态优先留待产品取舍。

原始卡片（不改写）：

- **林径步移**；卡片 ID：`82bfc3c3-e7eb-5961-ae72-dac0d6758f3c`；候选 ID：`250522b7-1e78-562f-b7b2-ed6bcbe5bee9`。
  > 青石小径蜿蜒入林，棕白狗背影随落叶起伏，苔痕斑驳的石阶与树影低垂，静默铺展成一方呼吸的节奏。
- **步履即风景**；卡片 ID：`f896e893-5507-5351-8542-885a6001fde3`；候选 ID：`4ff3d4b8-82bd-5d1b-835e-324c97a7052c`。
  > 棕白相间的狗沿青石小径渐行渐远，毛发蓬松，项圈轻晃，整条林径因此有了心跳的节奏。

相关素材（“全部抽帧”用于避免以单张预览代替完整证据）：

- [09ed75eff07f6aac0133ab3e542c4b3d.mp4](<OWNER_CONTROLLED_TEST_PACK_1/09ed75eff07f6aac0133ab3e542c4b3d.mp4>)；最终展示于：林径步移；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w00_7500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w01_1500.jpg>) · [帧 4](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_13a140ce-fe6b-48d5-813b-77031ecbebd8/frame_w01_7500.jpg>)。
- [6576b04fcedee8130e6c9d1650be78e0.mp4](<OWNER_CONTROLLED_TEST_PACK_1/6576b04fcedee8130e6c9d1650be78e0.mp4>)；最终展示于：林径步移、步履即风景；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_6522750f-ce02-4ede-8a12-a195e05012ee/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_6522750f-ce02-4ede-8a12-a195e05012ee/frame_w00_4500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_6522750f-ce02-4ede-8a12-a195e05012ee/frame_w00_7500.jpg>)。
- [c9a75a21437b5d5462cf39a8c0cbba28.mp4](<OWNER_CONTROLLED_TEST_PACK_1/c9a75a21437b5d5462cf39a8c0cbba28.mp4>)；最终展示于：林径步移；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w00_1500.jpg>) · [帧 2](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w00_7500.jpg>) · [帧 3](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w01_1500.jpg>) · [帧 4](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_1/round_1/evidence/asset_342021e1-340b-4ec9-8ef0-3d80e19612bc/frame_w01_7500.jpg>)。

你的评价：〔待填〕。可以直接反馈“R04，哪一个素材应移出/保留，以及原因”。

### R05｜四个骆驼素材去重后保留三个，Chapter不被连带删除

范围：素材包 2，S10。性质：应保护的已有正向能力。

四个候选成员中，最终保留10、11、13.jpg，12.jpg未展示。只保护合法子集交付，不认可全部动物属性、动作与时间表述。

检查目标：去重可以减至三个有贡献的素材；不因返回子集而删掉整个Chapter，也不强制每次选同一张。

原始卡片（不改写）：

- **驼群静立草野间**；卡片 ID：`384a7994-eb86-5113-a602-bab976729232`；候选 ID：`76e1a08f-4e43-51bc-be41-949d8b6bc40b`。
  > 多峰骆驼在开阔草地上或立或卧，其中一只背负双鞍居于中央，远处高压电塔与山峦勾勒出荒野中的生活图景。

相关素材（“全部抽帧”用于避免以单张预览代替完整证据）：

- [10.jpg](<OWNER_CONTROLLED_TEST_PACK_2/10.jpg>)；最终展示于：驼群静立草野间；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_2/round_1/evidence/asset_9fe84abc-8d5e-4dcf-8b77-a1865f300721/frame_w00_4500.jpg>)。
- [11.jpg](<OWNER_CONTROLLED_TEST_PACK_2/11.jpg>)；最终展示于：驼群静立草野间；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_2/round_1/evidence/asset_15302340-c165-47e4-8db3-502622148919/frame_w00_4500.jpg>)。
- [12.jpg](<OWNER_CONTROLLED_TEST_PACK_2/12.jpg>)；未在本案例卡片中展示；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_2/round_1/evidence/asset_d314a365-1afd-4a89-8f09-565ddcf3ed81/frame_w00_4500.jpg>)。
- [13.jpg](<OWNER_CONTROLLED_TEST_PACK_2/13.jpg>)；最终展示于：驼群静立草野间；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_2/round_1/evidence/asset_ee5db843-ac6b-42ba-8fb3-4c3922b289fe/frame_w00_4500.jpg>)。

你的评价：〔待填〕。可以直接反馈“R05，哪一个素材应移出/保留，以及原因”。

### R06｜夜间街边小吃有事实，但没有Aha资格

范围：素材包 2，AHA_ELIGIBILITY。性质：待评价的候选覆盖问题。

该素材在S04有STRONG事实、角色KEEP，事件分类却为NONE/NONE；当前Aha入口会排除。是否值得独立Aha尚无用户标签，不预填必须入选。

检查目标：候选覆盖与最终值得保留分开评价；无用户判断时不把漏入池直接计作用户价值损失。

相关素材（“全部抽帧”用于避免以单张预览代替完整证据）：

- [20.jpg](<OWNER_CONTROLLED_TEST_PACK_2/20.jpg>)；未在本案例卡片中展示；全部抽帧：[帧 1](<ORIGINAL_REPOSITORY/var/codex_v1_68_2_experience_first_chapter_execution/pack_2/round_1/evidence/asset_5111fc58-d949-4d13-8d11-359f7fadd4dc/frame_w00_4500.jpg>)。

你的评价：〔待填〕。可以直接反馈“R06，哪一个素材应移出/保留，以及原因”。

## 下一小步：只检验辅助组织提示的影响

先不改线上代码、不重写事实、不换模型、不改 Aha 数量或优先级。

建议对素材包 1、2 的**全部原观察**做同输入结构对照，不只发送上面六个挑选案例：

| 项目 | 对照 A | 候选 B |
| --- | --- | --- |
| 模型、输出格式、结构任务说明 | 保持已归档配置 | 完全相同 |
| 原事实、事实 ID、证据 ID、素材 ID、输入顺序与不可信时间声明 | 原样 | 原样 |
| 可用角色、Aha 原有资格范围与事件信息 | 原样 | 原样，不扩大 Aha 准入 |
| 场景/活动/episode/主体/motif 分类及预分 Moment | 保留 | 仅移除这一层辅助组织提示 |
| 输入范围 | 整包，不裁剪 | 同一整包，不裁剪 |
| 调用范围 | 仅结构步骤 | 仅结构步骤 |

这属于一个“有无辅助组织提示层”的对照，不能进一步把结果归因于其中某一个字段。保留事件信息是为了不混改 Aha 准入；也因此不能将本实验称为完全无类别输入。

建议正式执行时每个条件每包两次，共 8 次结构调用；A、B 交错运行并全部保留。两次仅能提供初步方向，不能证明稳定泛化。历史结果仅用于定位，不代替同时运行的对照 A。只要两包有一致改善方向，再做候选实现与完整新跑；若结果混合，不挑最好的一次、不立刻继续追加提示。

为什么不是再加一段“不能合并不同经历”：当前实际请求已经包含具体经历、禁止宽泛主题误合、不能按导入顺序推断连续等要求。先减少可能有干扰的输入层，比继续补同义要求更能定位原因。

本地准备不解除 V1.68 原候选的停止状态；后续属于独立诊断实验。结构对照不算完整验收，也不改变现有运行规则。完整验收仍从原素材开始执行所有已实现流程。

## 产品取舍先隔离，不阻塞这一步

- 无 Chapter 日是否可以有多个 Aha：沿用现状，本步不改。
- 同故事的 Chapter 与 Aha 谁优先：本步只记录重复，不擅自替用户选择。
- 第五 Chapter、Writer 风格和 20% 字数容差：本步不改。

因此这一小步不需要额外产品决策；完成对照后再结合真实变化集中讨论必要取舍。

## 本地核验与证据边界

基线 JSON 中的原始卡片/候选/事实均从归档文件提取；用户评分为 null。定位校验只检查 ID、文件与摘要，没有用代码替人给语义打分。正向图像判断继承 V1.68 已归档完整证据审阅，不声称本轮重新观看了所有视频。

后续若移除提示层没有改善，不应顺势断言需要新标签。应回到同一事实下的结构决策能力对照，并明确说明结果不足。
