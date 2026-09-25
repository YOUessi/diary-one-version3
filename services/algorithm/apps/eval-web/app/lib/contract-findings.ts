import type { ContractFinding, X01Editorial, X01Result } from "./contracts";
import { projectV041Memories } from "./result-contract";

export const canonicalTagLabels: Record<string, string> = {
  "ACTIVITY.WALKING": "步行",
  "ACTIVITY.CITY_WALK": "城市漫步",
  "ACTIVITY.CRAFT": "手作",
  "ACTIVITY.POTTERY": "陶艺",
  "ACTIVITY.SHARED_MEAL": "一起用餐",
  "SETTING.TRADITIONAL_HISTORIC_DISTRICT": "古镇街区",
  "SETTING.CAFE_OR_TEA_SHOP": "咖啡茶饮店",
  "SETTING.HOME": "家中",
  "SETTING.OUTDOOR_NATURE": "自然户外",
  "SETTING.WORKPLACE": "工作场所",
  "CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE": "传统建筑",
  "CENTRAL_SUBJECT.CAT": "猫咪",
  "CENTRAL_SUBJECT.DOG": "狗狗",
  "CENTRAL_SUBJECT.FOOD_OR_DESSERT": "食物甜点",
  "CENTRAL_SUBJECT.CRAFT_OBJECT": "手作作品",
  "OCCASION.TRAVEL_OUTING": "旅行出游",
  "OCCASION.BIRTHDAY": "生日",
  "OCCASION.FAMILY_GATHERING": "家庭相聚",
};

export function visibleLength(value: string) {
  return Array.from(value.replace(/\s/g, "")).length;
}

function sentenceCount(value: string) {
  const trimmed = value.trim();
  if (!trimmed) return 0;
  const endings = trimmed.match(/[。！？!?]+/g);
  return Math.max(1, endings?.length || 1);
}

function finding(
  severity: ContractFinding["severity"],
  code: string,
  message: string,
): ContractFinding {
  return { severity, code, message };
}

function editorialFindings(
  memory: X01Editorial,
  kind: "CHAPTER" | "AHA",
  selectedMediaCount: number,
  softAhaLength = false,
): ContractFinding[] {
  const findings: ContractFinding[] = [];
  if (kind === "CHAPTER") {
    if (selectedMediaCount < 3 || selectedMediaCount > 5) {
      findings.push(finding(
        "BLOCK",
        "CHAPTER_MEDIA_COUNT",
        `Chapter 使用了 ${selectedMediaCount} 个可见素材；当前要求 3–5 个，已取消双素材例外。`,
      ));
    }
    const titleLength = visibleLength(memory.title);
    if (titleLength < 2 || titleLength > 12) {
      findings.push(finding(
        "BLOCK",
        "ZH_TITLE_LENGTH",
        `标题为 ${titleLength} 个可见字符；中文测试合同为 2–10，确有必要时可到 12。`,
      ));
    } else if (titleLength > 10) {
      findings.push(finding(
        "REVIEW",
        "ZH_TITLE_SOFT_EXTENSION",
        `标题为 ${titleLength} 个字符，需要确认延长确有语义必要。`,
      ));
    }
    const storySentences = sentenceCount(memory.story);
    if (storySentences < 1 || storySentences > 2) {
      findings.push(finding(
        "BLOCK",
        "CHAPTER_STORY_SENTENCES",
        `Chapter 文案检测为 ${storySentences} 句；合同要求默认 1 句、最多 2 句。`,
      ));
    }
  } else {
    if (selectedMediaCount !== 1) {
      findings.push(finding(
        "BLOCK",
        "AHA_VISIBLE_MEDIA_COUNT",
        `Aha 关联了 ${selectedMediaCount} 个可见素材；合同要求恰好 1 个。`,
      ));
    }
    const lineLength = visibleLength(memory.story);
    if (lineLength < 1 || (!softAhaLength && lineLength > 20)) {
      findings.push(finding(
        "BLOCK",
        "AHA_MOMENT_LINE_LENGTH",
        softAhaLength ? "Aha 文案为空。" : `Aha Moment Line 为 ${lineLength} 个可见字符；该历史版本上限为 20。`,
      ));
    }
    if (softAhaLength && lineLength > 24) {
      findings.push(finding("REVIEW", "AHA_LENGTH_OVER_TOLERANCE_REVIEW",
        `Aha ${memory.id}：${lineLength} 字，偏长，待评价；保留原文，不按长度阻断。`));
    }
    if (sentenceCount(memory.story) > 1) {
      findings.push(finding("BLOCK", "AHA_SINGLE_PEAK", "Aha 应是一条单峰 Moment Line，不应写成多句小故事。"));
    }
  }

  const unknownTags = memory.tags.filter((tag) => !(tag in canonicalTagLabels));
  if (unknownTags.length) {
    findings.push(finding(
      "BLOCK",
      "UNREGISTERED_CANONICAL_TAG",
      `存在未注册 Tag：${unknownTags.join("、")}。测试结果不能写入长期记忆索引。`,
    ));
  }
  return findings;
}
export function evaluateLatestContract(result: X01Result): ContractFinding[] {
  const findings: ContractFinding[] = [];
  const { visibleChapters, visibleAhas } = projectV041Memories(result);
  const momentAssets = new Map(result.moments.map((moment) => [moment.id, moment.asset_ids]));
  const selectedAssets = (memory: X01Editorial) => new Set(
    memory.selected_media?.map((item) => item.asset_id)
      || memory.moment_ids.flatMap((id) => momentAssets.get(id) || []),
  );

  if (visibleChapters.length > 4) {
    findings.push(finding("BLOCK", "CHAPTER_DAILY_LIMIT", "常规测试日最多 4 个 Chapter；第 5 个需走例外 Gate。"));
  }
  if (visibleAhas.length > 3) {
    findings.push(finding("BLOCK", "AHA_DAILY_LIMIT", "一天最多 3 个 Aha。"));
  }
  visibleChapters.forEach((chapter) => {
    findings.push(...editorialFindings(chapter, "CHAPTER", selectedAssets(chapter).size));
  });
  visibleAhas.forEach((aha) => {
    const ahaAssets = selectedAssets(aha);
    findings.push(...editorialFindings(aha, "AHA", ahaAssets.size,
      result.decision_trace.runtime_policies?.writer_exit === "DIARY_ONE_X02_WRITER_EXIT_V02"));
    for (const chapter of visibleChapters) {
      const overlap = [...ahaAssets].some((assetId) => selectedAssets(chapter).has(assetId));
      if (overlap) {
        findings.push(finding(
          "REVIEW",
          "CHAPTER_AHA_NARRATIVE_INDEPENDENCE",
          "Aha 与 Chapter 共用素材。复用本身可以成立，但需要确认它们承担不同的故事职责。",
        ));
      }
    }
  });
  if (!visibleChapters.length && !visibleAhas.length) {
    findings.push(finding(
      "REVIEW",
      "NO_VISIBLE_MEMORY_TO_CHECK",
      "本轮没有正式可见记忆可做表面合同检查；诊断候选不会被当作已发布结果评分。",
    ));
  } else if (!findings.length) {
    findings.push(finding("PASS", "LATEST_VISIBLE_CONTRACT", "当前可见结果通过最新 Chapter/Aha 表面合同检查。"));
  }
  return findings;
}
