import { useEffect } from 'react';
import { AppState, type AppStateStatus } from 'react-native';

/** 进入后台或非 active 时回调（用于暂停媒体，返回不自动续播）。 */
export function useAppBackgroundPause(onPause: () => void) {
  useEffect(() => {
    const sub = AppState.addEventListener('change', (state: AppStateStatus) => {
      if (state !== 'active') onPause();
    });
    return () => sub.remove();
  }, [onPause]);
}
