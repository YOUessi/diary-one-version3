import type { X01Editorial, X01Result } from "./contracts";

/** Match the delivered surface, never a rejected draft or a fallback-generation row. */
export function ahaLengthReview(memory: X01Editorial, result: X01Result) {
  const entries = result.decision_trace.writer_items.filter((item) => (
    item.candidate_id === memory.candidate_id
    && item.memory_type === "AHA"
    && item.surface_source === memory.surface_source
    && item.validation_status === "PASSED"
    && item.writer_exit_policy_version === "DIARY_ONE_X02_WRITER_EXIT_V02"
    && (item.validation_scope === "FORMAT_AND_REFERENCES_ONLY_NOT_SEMANTIC_VERIFICATION"
      || item.validation_scope === "COMPLETE_FACT_COPY_FORMAT_AND_REFERENCES")
  ));
  const entry = entries.at(-1);
  if (!entry?.length_review_required
    || entry.length_status !== "OVER_TOLERANCE_REVIEW"
    || !entry.quality_flags?.includes("AHA_LENGTH_OVER_TOLERANCE_REVIEW")) return null;
  return { label: "偏长，待评价", characters: entry.text_visible_characters };
}
