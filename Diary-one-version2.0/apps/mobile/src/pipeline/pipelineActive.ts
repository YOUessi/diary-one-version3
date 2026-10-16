import type { PipelineTask } from './types';

export function isPipelineActive(tasks: PipelineTask[]): boolean {
  return tasks.some((t) => t.status !== 'succeeded' && t.status !== 'failed');
}

export function activePipelineTask(tasks: PipelineTask[]): PipelineTask | undefined {
  return tasks.find((t) => t.status !== 'succeeded' && t.status !== 'failed');
}
