/**
 * 本地素材账本（S6+）：当前为内存 + 文件系统 Bundle；
 * 后续可换 expo-sqlite 持久化 asset_id / sha256 / pipeline task。
 */
import type { PipelineTask } from '../pipeline/types';

const taskLog: PipelineTask[] = [];

export function rememberPipelineTask(task: PipelineTask) {
  taskLog.unshift(task);
  if (taskLog.length > 20) taskLog.pop();
}

export function listRecentPipelineTasks(): PipelineTask[] {
  return [...taskLog];
}
