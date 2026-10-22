import { create } from 'zustand';

/** Transient UI only: never persisted with the account or diary. */
export type ImportFeedback = {
  kind: 'busy' | 'confirm' | 'error' | 'notice';
  title: string;
  message: string;
  dismiss: () => void;
  dismissLabel?: string;
  confirm?: { label: string; run: () => void };
};

export const useImportFeedbackStore = create<{ feedback: ImportFeedback | null }>(() => ({
  feedback: null,
}));

export function clearImportFeedback() {
  useImportFeedbackStore.setState({ feedback: null });
}
