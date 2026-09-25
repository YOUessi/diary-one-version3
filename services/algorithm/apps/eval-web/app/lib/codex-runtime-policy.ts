export const CURRENT_RUNTIME_POLICIES = {
  chapter_selection_response: "DIARY_ONE_X02_CHAPTER_SELECTION_RESPONSE_V02",
  aha_pair_conflict: "DIARY_ONE_X02_AHA_PAIR_CONFLICT_V02",
  content_brief: "DIARY_ONE_X02_CONTENT_BRIEF_V01",
  writer_exit: "DIARY_ONE_X02_WRITER_EXIT_V02",
  subject_granularity: "DIARY_ONE_X02_SUBJECT_GRANULARITY_V02",
} as const;

export function currentRuntimePolicies(value: unknown): boolean {
  if (!value || typeof value !== "object") return false;
  const fields = value as Record<string, unknown>;
  return Object.entries(CURRENT_RUNTIME_POLICIES).every(([key, version]) => fields[key] === version);
}

export function runtimePolicyLabel(value: unknown): string {
  return currentRuntimePolicies(value)
    ? "动物通用分类 V02 · 精选接收 V02 · Aha 去重 V02 · 单次 Writer / 软长度 V02"
    : "未确认当前策略；不能当作新版本运行";
}
