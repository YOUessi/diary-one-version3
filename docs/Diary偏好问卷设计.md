# Diary 偏好问卷设计

## 1. 文档信息

| 项目 | 内容 |
| --- | --- |
| 文档版本 | v1.5 |
| 适用阶段 | 注册后首次使用、用户偏好与个人 Tag 初始化 |
| 建议时长 | 约 1–2 分钟；第一题中的自然语言补充入口可跳过 |
| 核心目标 | 通过六个同层级的时刻主题建立初始偏好，并允许用户补充具体兴趣 Tag |

## 2. 设计结论

问卷开场不直接询问“你有什么爱好”，也不要求用户理解“人物、活动、地点”等标签维度，而是先用六张同层级、可多选的卡片了解用户希望保留的时刻主题。第一题另设 `Something else` 作为自然语言补充入口，以及 `No preference — follow my day` 供用户明确表示暂不设置正向偏好。

> 用户选择时刻主题，不等于选择该主题下的全部具体 Tag；用户不需要理解 Tag 体系。

需要区分两类信号：**时刻偏好**回答“哪些已拍到的内容更值得成为记忆”；**兴趣 Tag**回答“用户希望系统认识哪些稳定兴趣或具体活动词汇”。兴趣 Tag 可以改善词库匹配和排序，但本身不是素材证据，也不代表这些活动实际发生过。

“人物、活动、地点、事物”属于后台标签体系，不应成为前台问卷的作答步骤。用户可以同时希望记录人、事情和地点，不需要在这些维度之间做取舍。

## 3. 设计原则

1. **允许多选**：不要求用户只选一种生活主题。
2. **可以跳过**：问卷不是进入产品的强制门槛。
3. **随时可改**：所有结果均写入可查看、可编辑、可删除的用户画像卡。
4. **选择时刻主题，不选择标签分类**：前台的六张卡片保持同一抽象层级；后台用主题偏好匹配已被素材证实的 Tag，不把主题自动拆成用户明确选择的具体 Tag。
5. **不制造事实**：偏好只改变已有内容的筛选、排序和表述，不允许补充素材中不存在的内容。
6. **逐步完善**：首次问卷只建立粗粒度偏好，具体人物、地点和活动在后续使用中逐渐补充。
7. **偏好与隐私分离**：“少出现”是推荐权重，“绝不使用”是隐私规则，不能混为一谈。
8. **不把兴趣调查变成画像盘问**：自然语言补充是第一题中的可选入口，不是独立必答题；可输入、可搜索、可多选，不要求用户选“最喜欢”的单一爱好，也不把 Tag 维度作为必答分类。

## 4. 问卷整体流程

```text
问卷说明
  ↓
第一题：选择希望多记录的时刻主题（六张主题卡 + Something else + No preference）
  ├─ 选中 Something else → 第一题补充页：自然语言或 Tag 搜索（可跳过）
  └─ 未选中 Something else（包括选择 No preference）→ 直接进入第二题
  ↓
第二题：选择希望少出现的内容
  ↓
确认系统理解结果
  ↓
生成用户画像卡
```

## 5. 开场页

### 页面标题

Help Diary get to know you

### 页面说明

Choose the moments you would like to remember. Diary only works with what was actually captured and will not make up anything that did not happen.

### 辅助说明

- Takes about 1–2 minutes
- You can skip this step
- You can change these preferences anytime

### 操作

- 主按钮：`Get started`
- 次按钮：`Skip for now`

## 6. 第一题：希望多记录的时刻

### 题目

Which kinds of moments would you like Diary to notice more?

### 辅助文案

Choose as many as you like. You can change these anytime.

### 选项

| 时刻主题卡                  | 面向用户的解释                                            | 偏好作用范围与相关素材 Tag 示例                                                                                                                                                                             |
| ---------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| People who matter      | Time with family, friends, and people close to you | 只记录“重要的人际时刻”这一宽泛主题偏好。素材中的 `participant.family`、`participant.friend` 和 `activity.parent_child_time`、`activity.family_gathering` 可在关系已确认、内容有证据时参与匹配；选择本卡不等于用户同时声明喜欢“家人”和“朋友”，也不生成通用“people” Tag。 |
| Time with pets         | The moments you share with your pets               | 只记录宠物时刻主题偏好；有证据时可匹配 `participant.pet`、`activity.pet_activity`。选择本卡不证明素材中已经出现宠物。                                                                                                                |
| Travel & exploring     | Trips, city walks, and places you discover         | 只记录出行探索主题偏好；有证据时可匹配 `activity.travel`、`activity.city_walk`、`activity.cultural_exploration`。不据此把每一种旅行子活动写成用户明确偏好。                                                                               |
| Sports & movement      | Hikes, runs, rides, and other active moments       | 只记录运动与身体活动主题偏好；有证据时可匹配 `activity.sport`、`activity.hiking`、`activity.running`、`activity.cycling`、`activity.skateboarding`。不据此断言用户偏好全部运动。                                                        |
| Creative activities    | Making, painting, and working on projects          | 只记录创作性活动主题偏好；有证据时可匹配 `activity.diy`、`activity.painting`，创作/制作证据明确时也可涉及 `activity.trade_work`。不默认将 `activity.cooking` 归入本卡。                                                                     |
| Nature & living things | Landscapes, plants, and wildlife                   | 只记录自然景观与生物主题偏好；有证据时可匹配 `subject.landscape`、`subject.plant`、`subject.wildlife` 及其适用细分词。看到植物不等于发生园艺活动，也不由自然主题推断任何具体活动偏好。                                                                         |
| Something else | Tell Diary in your own words | 第一题的补充入口，不是第七个主题；不生成 `theme_id`，选择后进入紧接本题的自然语言补充页。 |
| No preference — follow my day | Let Diary decide based on what actually happened | 明确表示本题暂不设置正向主题或具体兴趣偏好；不生成内容 Tag 或 `theme_id`。 |

前六张卡片表达的是同层级的时刻主题，不是 Tag 库新增的六个标准内容词条；`Something else` 是补充入口，`No preference — follow my day` 是明确的无偏好回答，两者都不是新主题。表中 Tag 只是后续匹配素材时可能参考的现有词；用户选中主题卡时，仅写入对应的主题偏好，不批量写入这些具体 Tag 的“喜欢”关系，也不将偏好写成素材事实。

### 交互规则

- 六张主题卡均可多选，不按“人物、事情、地点”分步骤；例如可同时选择 `People who matter` 与 `Creative activities`。
- `Something else` 可单独选择，也可与任意主题卡同时选择。点击 `Continue` 后，若选中该项，先进入自然语言补充页，再进入第二题；未选中则直接进入第二题。已经选择的主题卡须保留。
- `No preference — follow my day` 与六张主题卡及 `Something else` 互斥：选中它会取消其他选择；之后再选任意主题卡或 `Something else`，则取消无偏好选项。
- 用户日后把第一题改为无偏好时，仅撤销或停用本题产生的正向主题及具体兴趣偏好，不删除其在其他入口主动添加的偏好。
- 不强制规定选择数量，建议界面提示 `Just pick the ones that feel right.`。
- 本题主题卡表达“值得记录的时刻主题”，不是用户的完整兴趣画像；具体兴趣词汇只能通过 `Something else` 补充或后续设置明确添加。
- `No preference — follow my day` 表示用户明确选择“暂不设置正向偏好”；未选择任何选项就跳过表示“未回答”。若只选择 `Something else`、随后留空跳过补充页，也视为未回答。两者都不创建正向偏好，但必须在问卷回答状态中区分。
- 每张主题卡可以配一张代表性图片，减少文字阅读成本。
- 主题卡只建立初始偏好，不承诺每天一定生成对应内容。

### 自然语言补充页（由第一题的 `Something else` 进入）

#### 页面标题

Anything else you’d like Diary to remember?

#### 辅助文案

Optional. Add an activity, interest, person, or place in your own words. For example: weekend fishing, city walks, model-building, or walks by the sea with Dou Dou.

#### 输入方式

- 自然语言输入框；可选的标准 Tag 搜索与推荐优先支持 `activity`，也允许搜索参与者、对象和环境词。
- 用户可以补充多个具体词或组合表达，不要求先选择人物、活动或地点分类。
- 提供 `Continue` 与 `Skip for now`；即使从 `Something else` 进入，留空或跳过也不产生空偏好记录，不影响已选择的主题卡。

#### 解析示例

用户输入：

> I would like to remember walks by the sea with Dou Dou.

系统解析候选（仅为用户偏好候选，尚不表示素材中已经发生）：

```text
Participant: participant.pet（仅在用户确认 Dou Dou 是宠物后）
Setting: setting.waterside；如素材主体是海景，可另匹配 subject.ocean_view
Activity: activity.city_walk（仅当语义确为城市漫步；否则不强行套用）
Private entity: Dou Dou（名字不进入公共 Tag 词库）
Preference scope: Dou Dou × waterside × matched activity
```

如果“Dou Dou”的类型不明确，系统只在确有必要时用一句上下文问题消歧；不展示完整的 Tag 维度分类题。例如：

> Is Dou Dou your pet?

- Yes
- No, keep the name as a private preference
- Skip for now

#### 匹配规则

1. 优先匹配 Tag 自建库中的标准词和别名，并使用稳定 `tag_id`；搜索与语义匹配不要求用户浏览五个逻辑大类。
2. 返回 1–3 个候选正向偏好 Tag，以可移除/可修改的标签形式让用户确认；高置信度匹配也不得变成素材事实。
3. 含义不明确时，只对影响归类的具体词做必要确认；用户可跳过并保留原始表达。
4. 用户搜索/添加兴趣时，优先选择现有活动 Tag（如 `activity.fishing`、`activity.city_walk`、`activity.diy`），并将其作为用户正向偏好关系保存；不另建 `interest_seed` Tag 类别。
5. 词库未覆盖的表达先保留为私有偏好原文或别名候选，不自动扩充公共标准词库；后续达到真实需求后再审核归并。
6. AI 可以负责拆解和召回候选，但不能自行定义正式公共标签体系。

## 7. 第二题：希望少出现的内容

### 题目

What would you like to see less often?

### 辅助文案

This only makes these moments less likely to become featured memories. It will not delete your original content.

### 选项

| 选项 | 建议的偏好原因 ID 与作用范围（均不是内容 Tag） |
| --- | --- |
| Repetitive commutes | `repetitive_commute`；通勤语义 + 一段时间内相似路线/片段重复出现。通勤是后台内容特征，不假设词库已有 `activity.commute` |
| Long work sessions or meetings | `long_low_density_work`；工作/会议语义 + 片段时长、动作/场景变化少等特征 |
| Too many similar moments | `similar_moments`；作用于时间范围内的视觉/语义相似度与已展示次数，不绑定某个活动 Tag |
| Everyday meals | `routine_meals`；匹配用餐/做饭内容及其重复频率，不因出现食物就降低优先级 |
| Landscape-only scenes | `landscape_only`；风景主体占比高且没有显著人物动作/事件时降低优先级，不把“没有人物”建成内容 Tag |
| Repetitive indoor routines | `repetitive_indoor_routine`；室内环境 + 活动/片段相似度及变化程度，不假设 `home` 或 `workshop` 是现有地点 Tag |
| Something I’d rather not revisit (optional) | `uncomfortable_content`；仅由用户直接选择/描述并保存用户原意，不由模型猜测不适原因 |
| Nothing for now | 不建立回避规则 |

以上 `preference_reason_id` 是偏好关系中的建议稳定枚举，不属于 Tag 词库。是否在 1.0 首次问卷中呈现 `Something I’d rather not revisit` 可通过用户研究决定；如保留，应允许用户不说明原因并随时撤回。

### 交互规则

- 支持多选。
- `Nothing for now` 与本题其他选项互斥；选中它会取消已选的回避原因，之后再选任一回避原因则取消 `Nothing for now`。
- 结果写入 `preference_polarity=avoid`、`preference_reason_id`、`target_scope` 和 `strength`，而不是负向内容 Tag 或内容删除规则。
- 系统再依据素材 Tag、时长、相似度、动作/场景变化等后台证据解释回避原因；这些特征不暴露为问卷 Tag。
- 正向与负向偏好可以共存；更具体的负向组合只降低对应组合的优先级，不应覆盖更宽泛的正向偏好。例如“喜欢家庭日常，但少展示重复的日常餐食”。
- 如果用户希望某类内容“绝不上传、绝不生成或绝不分享”，应引导进入独立的隐私设置流程。

## 8. 结果确认页

### 页面标题

Here is what Diary will look out for

### 展示示例

```text
Notice more
People who matter · Travel & exploring

Show less often
Repetitive commutes · Similar moments

Activities and interests you asked Diary to recognize
Fishing · City walks · Model building
```

### 说明文案

These preferences only affect how your content is selected and presented. Diary will only use moments that were actually captured and supported by the available content.

确认页将“想多记录的时刻”“希望少出现的内容”和“用户选择的活动/兴趣 Tag”分组展示，避免把偏好声明误呈现为素材事实。负向分组展示用户选择的回避原因，不显示成被拉黑的内容 Tag。摘要必须严格按本次已确认的 Tag 与偏好规则生成，不得自行补充用户未选的兴趣、人物或场景，也不得遗漏用户已选项目。活动/兴趣分组可显示：

如果第一题选择了 `No preference — follow my day`，`Notice more` 分组显示该选项的文案，不生成虚构的主题或具体兴趣；如果是跳过第一题，则不把跳过显示为用户主动选择“无偏好”。

> These interests help Diary recognize relevant moments when they appear in your captured content.

### 操作

- 主按钮：`Confirm and continue`
- 次按钮：`Go back and edit`
- 文本入口：`You can change this later in Settings`

## 9. Tag 写入规则

### 9.1 主题卡与具体 Tag 偏好分开记录

用户选择 `People who matter` 与 `Sports & movement`，只能说明希望 Diary 留意这两类时刻，不能直接推导为用户喜欢 `participant.family`、`participant.friend`、`activity.hiking`、`activity.running` 等每一个具体 Tag，更不能推导出“和家人徒步”的组合偏好。

只有用户通过第一题的 `Something else` 入口明确选择或确认具体词，或后续基于真实内容明确表达组合意图时，才建立相应的具体 Tag 或组合偏好。例如：

```text
第一题选择 People who matter + Sports & movement → 两条独立的主题偏好
第一题补充页明确添加 Hiking → `activity.hiking` 的具体正向偏好
用户明确表示“多记录和家人徒步的时刻”且关系已确认 → `participant.family` + `activity.hiking` 的组合偏好
```

### 9.2 建议的数据结构

| 字段 | 说明 |
| --- | --- |
| `question_1_response` | 第一题回答状态 `selected` / `no_preference` / `skipped`：分别表示确认了主题或具体补充、明确选择无偏好、未回答；不属于内容 Tag |
| `theme_id` | 第一题六个主题之一；主题偏好使用，和标准内容 `tag_id` 分开 |
| `tag_id` | 可选的标准 Tag 目标；只表示偏好作用范围，不表示素材关联 |
| `preference_polarity` | `like` / `avoid`；负向选择表达回避体验，不创建负向 Tag |
| `preference_reason_id` | 用户可理解的回避原因；负向偏好必填，正向偏好可为空或使用经产品确认的原因值 |
| `target_scope` | 单个 Tag、Tag 组合或后台内容特征条件 |
| `strength` | 偏好强度 |
| `source` | 首次问卷、用户手动添加、行为学习等 |
| `confidence` | 自然语言到标准 Tag/作用范围的匹配置信度 |
| `updated_at` | 最近更新时间 |

同一个 `tag_id` 可以同时出现在素材关联与用户偏好作用范围中，但两者必须是独立记录：素材 Tag 表示“素材里有证据支持”，用户偏好表示“用户声明希望系统关注/少看”。用户添加的兴趣词不得反向写成素材 Tag；负向原因也不得写进内容 Tag 词库。

主题偏好、具体 Tag 偏好和组合偏好需要分别保留来源与作用范围。选择 `No preference — follow my day` 时只记录第一题的明确回答状态，不创建正向主题偏好或具体 Tag 偏好，也不将其理解为负向偏好。组合偏好需要额外记录多个 Tag 的关联关系，不能只保存为互相独立的单 Tag；同时选择两张主题卡本身也不构成组合偏好。

### 9.3 权重原则

- 用户明确选择的偏好权重高于系统通过行为推断的偏好。
- 用户明确表达的具体组合偏好可以高于宽泛主题偏好；不能由主题卡自动拆出具体 Tag 偏好。
- “减少出现”存成 `avoid` 偏好原因与作用范围，不等同于屏蔽，也不生成负向 Tag。
- “绝不使用”属于强约束，不进入普通权重计算。
- 用户单次删除、跳过或未分享内容，不应直接推断为讨厌其中全部 Tag。

## 10. 使用后的渐进式完善

首次问卷只负责建立偏好起点。产品应在出现真实内容后，通过低打扰方式逐步确认更具体的偏好。

示例：

> You often keep moments from walks with Dou Dou. Would you like Diary to notice more moments like these?

操作：

- `Notice more`
- `Keep it as it is`
- `Show fewer moments like this`

此时用户有真实素材作为参照，比首次使用时从大量抽象标签中选择更容易。

## 11. 不应放入本问卷的内容

以下内容应由其他流程处理：

| 内容 | 推荐位置 |
| --- | --- |
| 云端素材处理同意 | 独立的知情同意页面 |
| 人脸或声纹授权 | 首次使用人物功能时 |
| 通知偏好 | 通知权限申请前或设置页 |
| 分享格式偏好 | 分享功能首次使用时，或通过真实行为判断 |
| 敏感内容排除 | 独立隐私设置 |
| 具体人物身份绑定 | 有真实人物素材后再进行 |

## 12. 验收标准

问卷上线前至少应满足以下条件：

- 用户可以在不理解 Tag 概念的情况下完成设置。
- 用户可以同时表达对人物、活动和地点的偏好。
- 用户可不选 `Something else` 直接进入第二题；如选择该项，能用自然语言或搜索词条补充兴趣，也能留空跳过，不必理解后台维度。
- 用户可选择 `No preference — follow my day`；它与第一题其他选项互斥，且在回答状态上与跳过第一题明确区分。
- 时刻偏好、兴趣词汇和内容事实在存储与呈现上保持区分。
- 问卷可在约 1–2 分钟内完成；兴趣搜索和自然语言补充均可跳过。
- 第一题六张主题卡都能映射到明确的主题偏好及素材匹配范围，但不自动写入范围内的具体 Tag 偏好；`Something else` 只进入补充页，不创建主题偏好；补充页用户确认的具体词能映射到标准 Tag 或保留为私有原文。
- 自然语言匹配结果可以被用户查看和纠正。
- 偏好不会被系统当成素材中已经发生的事实。
- 负向偏好、隐私排除和内容删除在产品与数据层均保持独立。
- 用户可以在设置中查看、修改和删除画像卡内容。

## 13. 界面与原型流程校对

- 问卷只有两道常规问题；自然语言补充是第一题的 `Something else` 条件分支，结果确认不是第三题。补充页返回第一题时应保留此前已选的主题卡。
- 第一题和第二题的初始状态均不预选任何选项。原型中带黑色描边的卡片用于展示选择后的示例状态，不代表产品默认替用户作答。
- `BACK` 返回当前分支的上一步；`Skip setup for now` 退出整个设置流程；自然语言补充页的 `Skip this step` 只跳过补充，保留第一题已确认的主题选择。
- 第一题明确选择 `No preference — follow my day`、第一题跳过未作答、第二题选择 `Nothing for now` 是三种不同状态；确认页不能把“跳过”呈现为用户主动选择“无偏好”。
- 多选卡片、文本输入和 Tag 搜索在 Figma 中展示代表性状态与主要跳转路径；真实产品仍须按以上互斥、保留、清除和确认规则实现任意选择组合。
