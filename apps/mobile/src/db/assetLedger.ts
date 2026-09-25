import type { PipelineTask } from '../pipeline/types';

export type AssetLedgerEntry = {
  taskId: string;
  recordedAt: string;
  dayRevisionId?: string;
  intakeSource?: PipelineTask['intakeSource'];
  bundleVersion?: string;
  bundleJsonPath?: string;
  dayKey: string;
  sourceCount: number;
  status: PipelineTask['status'];
};

const MAX = 30;
let entries: AssetLedgerEntry[] = [];

export function recordPipelineLedger(task: PipelineTask) {
  entries = [
    {
      taskId: task.id,
      recordedAt: new Date().toISOString(),
      dayRevisionId: task.dayRevisionId,
      intakeSource: task.intakeSource,
      bundleVersion: task.bundleVersion,
      bundleJsonPath: task.bundleJsonPath,
      dayKey: task.dayKey,
      sourceCount: task.sourceCount,
      status: task.status,
    },
    ...entries.filter((e) => e.taskId !== task.id),
  ].slice(0, MAX);
}

export function listAssetLedger(): AssetLedgerEntry[] {
  return [...entries];
}

export function hydrateAssetLedger(saved: AssetLedgerEntry[] | undefined) {
  if (saved?.length) entries = saved.slice(0, MAX);
}

export function serializeAssetLedger(): AssetLedgerEntry[] {
  return [...entries];
}
