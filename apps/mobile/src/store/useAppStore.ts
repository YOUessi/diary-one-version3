import { create } from 'zustand';

import type {

  TodayStatus,

  Chapter,

  SmallMemory,

  Topic,

  MemoryPreference,

  CapturedOriginal,

} from '../model';

import type { PipelineTask } from '../pipeline/types';

import { diaryTodayKey } from '../domain/dayKey';

import { DEFAULT_LOCAL_PROFILE, type LocalProfile } from '../domain/localProfile';

import {

  DEFAULT_LANGUAGE,

  DEFAULT_MEMORY_LANGUAGE,

  DEFAULT_AUTOMATIC_CAPTURE_MODE,

  DEFAULT_NOTIFICATION_SETTINGS,

  type AutomaticCaptureMode,

  type LanguagePreference,

  type MemoryLanguagePreference,

  type NotificationSettings,

} from '../domain/appSettings';

import type { BundleExportVersion } from '../pipeline/bundleTypes';
import type { CloudProcessingTarget } from '../backend/types';

import {

  seedChapters,

  seedSmallMemories,

  seedTopics,

  seedPreferences,

  seedCaptured,

} from '../model';



export type DeviceLinkState = 'disconnected' | 'lab_linked';



type AppState = {

  todayStatus: TodayStatus;

  calendarExpanded: boolean;

  selectedDateKey: string;

  chapters: Chapter[];

  smallMemoriesByDate: Record<string, SmallMemory[]>;

  topics: Topic[];

  preferences: MemoryPreference[];

  capturedOriginals: CapturedOriginal[];

  pipelineTasks: PipelineTask[];

  researchEndpoint: string;

  researchToken: string;

  productionApiBaseUrl: string;

  productionApiToken: string;

  /** OTP verify 返回的会话令牌（持久化；API 仍可用 Dev Lite Bearer） */
  sessionToken: string;

  cloudProcessingTarget: CloudProcessingTarget;

  localProfile: LocalProfile;

  historyVisibleCount: number;

  historyLoadState: 'idle' | 'loading' | 'failed';

  historyLoadFailAlternate: boolean;

  deviceLinkState: DeviceLinkState;

  devicePendingRecordings: boolean;

  /** Set only when hardware reports level; never fabricated for Figma demos. */
  deviceBatteryPercent: number | null;

  lastSyncedAt: string | null;

  notificationSettings: NotificationSettings;

  language: LanguagePreference;

  memoryLanguage: MemoryLanguagePreference;

  automaticCaptureMode: AutomaticCaptureMode;

  bundleExportVersion: BundleExportVersion;

  onboardingComplete: boolean;

  /** Figma Daily Recap readiness changed — transient UI on Diary home. */
  dailyRecapShareBlockedBanner: boolean;

  setTodayStatus: (s: TodayStatus) => void;

  setResearchEndpoint: (url: string) => void;

  setResearchToken: (token: string) => void;

  setProductionApiBaseUrl: (url: string) => void;

  setProductionApiToken: (token: string) => void;

  setSessionToken: (token: string) => void;

  setCloudProcessingTarget: (target: CloudProcessingTarget) => void;

  setLocalProfile: (profile: LocalProfile) => void;

  setDeviceLinkState: (state: DeviceLinkState) => void;

  setNotificationSettings: (settings: NotificationSettings) => void;

  setLanguage: (language: LanguagePreference) => void;

  setMemoryLanguage: (language: MemoryLanguagePreference) => void;

  setAutomaticCaptureMode: (mode: AutomaticCaptureMode) => void;

  setBundleExportVersion: (version: BundleExportVersion) => void;

  setOnboardingComplete: (complete: boolean) => void;

  setDailyRecapShareBlockedBanner: (visible: boolean) => void;

  loadMoreHistory: () => void;

  setCalendarExpanded: (v: boolean) => void;

  setSelectedDateKey: (key: string) => void;

  calendarDayPreparing: boolean;

  selectDateKeyWithPrepare: (key: string) => void;

  updateYourStory: (chapterId: string, text: string | undefined) => void;

  addPreference: (title: string, text: string) => void;

  updatePreference: (id: string, title: string, text: string) => void;

  removePreference: (id: string) => void;

  removeCapturedOriginal: (id: string) => void;

  setPipelineTasks: (tasks: PipelineTask[]) => void;

  replaceStateFromBootstrap: (partial: Partial<AppState>) => void;

};



export const useAppStore = create<AppState>((set) => ({

  todayStatus: 'READY',

  calendarExpanded: false,

  selectedDateKey: diaryTodayKey(),

  chapters: seedChapters,

  smallMemoriesByDate: seedSmallMemories,

  topics: seedTopics,

  preferences: seedPreferences,

  capturedOriginals: seedCaptured,

  pipelineTasks: [],

  researchEndpoint: '',

  researchToken: '',

  productionApiBaseUrl: '',

  productionApiToken: '',

  sessionToken: '',

  cloudProcessingTarget: 'research',

  localProfile: DEFAULT_LOCAL_PROFILE,

  historyVisibleCount: 3,

  historyLoadState: 'idle',

  historyLoadFailAlternate: false,

  deviceLinkState: 'disconnected',

  devicePendingRecordings: false,

  deviceBatteryPercent: null,

  lastSyncedAt: null,

  notificationSettings: DEFAULT_NOTIFICATION_SETTINGS,

  language: DEFAULT_LANGUAGE,

  memoryLanguage: DEFAULT_MEMORY_LANGUAGE,

  automaticCaptureMode: DEFAULT_AUTOMATIC_CAPTURE_MODE,

  bundleExportVersion: 'V04',

  onboardingComplete: true,

  dailyRecapShareBlockedBanner: false,

  setTodayStatus: (todayStatus) => set({ todayStatus }),

  setDailyRecapShareBlockedBanner: (dailyRecapShareBlockedBanner) =>
    set({ dailyRecapShareBlockedBanner }),

  setResearchEndpoint: (researchEndpoint) => set({ researchEndpoint }),

  setResearchToken: (researchToken) => set({ researchToken }),

  setProductionApiBaseUrl: (productionApiBaseUrl) => set({ productionApiBaseUrl }),

  setProductionApiToken: (productionApiToken) => set({ productionApiToken }),

  setSessionToken: (sessionToken) => set({ sessionToken }),

  setCloudProcessingTarget: (cloudProcessingTarget) => set({ cloudProcessingTarget }),

  setLocalProfile: (localProfile) => set({ localProfile }),

  setDeviceLinkState: (deviceLinkState) =>

    set({

      deviceLinkState,

      devicePendingRecordings: deviceLinkState === 'lab_linked',

      todayStatus:

        deviceLinkState === 'lab_linked' ? 'READY_NEW_RECORDINGS' : 'READY',

    }),

  setNotificationSettings: (notificationSettings) => set({ notificationSettings }),

  setLanguage: (language) => set({ language }),

  setMemoryLanguage: (memoryLanguage) => set({ memoryLanguage }),

  setAutomaticCaptureMode: (automaticCaptureMode) => set({ automaticCaptureMode }),

  setBundleExportVersion: (bundleExportVersion) => set({ bundleExportVersion }),

  setOnboardingComplete: (onboardingComplete) => set({ onboardingComplete }),

  loadMoreHistory: () => {

    const state = useAppStore.getState();

    if (state.historyLoadState === 'loading') return;

    set({ historyLoadState: 'loading' });

    setTimeout(() => {

      const s = useAppStore.getState();

      const todayKey = diaryTodayKey();

      const pastCount = s.chapters.filter((c) => c.dateKey !== todayKey).length;

      if (s.historyVisibleCount >= pastCount) {

        set({ historyLoadState: 'idle' });

        return;

      }

      if (s.historyLoadFailAlternate) {

        set({ historyLoadState: 'failed', historyLoadFailAlternate: false });

        return;

      }

      set({

        historyVisibleCount: s.historyVisibleCount + 2,

        historyLoadState: 'idle',

        historyLoadFailAlternate: true,

      });

    }, 650);

  },

  removeCapturedOriginal: (id) =>

    set((state) => ({

      capturedOriginals: state.capturedOriginals.filter((c) => c.id !== id),

    })),

  setCalendarExpanded: (calendarExpanded) => set({ calendarExpanded }),

  setSelectedDateKey: (selectedDateKey) => set({ selectedDateKey, calendarDayPreparing: false }),

  calendarDayPreparing: false,

  selectDateKeyWithPrepare: (key) => {

    const current = useAppStore.getState().selectedDateKey;

    if (key === current) return;

    set({ calendarDayPreparing: true, selectedDateKey: key });

    setTimeout(() => {

      set({ calendarDayPreparing: false });

    }, 480);

  },

  updateYourStory: (chapterId, text) =>

    set((state) => ({

      chapters: state.chapters.map((c) =>

        c.id === chapterId ? { ...c, yourStory: text } : c,

      ),

    })),

  addPreference: (title, text) =>

    set((state) => ({

      preferences: [

        ...state.preferences,

        { id: `p-${Date.now()}`, title: title.trim(), text: text.trim() },

      ],

    })),

  updatePreference: (id, title, text) =>

    set((state) => ({

      preferences: state.preferences.map((p) =>

        p.id === id ? { ...p, title: title.trim(), text: text.trim() } : p,

      ),

    })),

  removePreference: (id) =>

    set((state) => ({

      preferences: state.preferences.filter((p) => p.id !== id),

    })),

  setPipelineTasks: (pipelineTasks) => set({ pipelineTasks }),

  replaceStateFromBootstrap: (partial) => set(partial),

}));



export function chaptersForDate(chapters: Chapter[], dateKey: string) {

  return chapters.filter((c) => c.dateKey === dateKey);

}



export function smallMemoriesForDate(

  map: Record<string, SmallMemory[]>,

  dateKey: string,

) {

  return map[dateKey] ?? [];

}



export function buildPersistedSlice(state: AppState) {

  return {

    chapters: state.chapters,

    smallMemoriesByDate: state.smallMemoriesByDate,

    topics: state.topics,

    preferences: state.preferences,

    localProfile: state.localProfile,

    researchEndpoint: state.researchEndpoint,

    researchToken: state.researchToken,

    productionApiBaseUrl: state.productionApiBaseUrl,

    productionApiToken: state.productionApiToken,

    sessionToken: state.sessionToken,

    cloudProcessingTarget: state.cloudProcessingTarget,

    capturedOriginals: state.capturedOriginals,

    todayStatus: state.todayStatus,

    pipelineTasks: state.pipelineTasks,

    deviceLinkState: state.deviceLinkState,

    devicePendingRecordings: state.devicePendingRecordings,

    lastSyncedAt: state.lastSyncedAt,

    notificationSettings: state.notificationSettings,

    language: state.language,

    memoryLanguage: state.memoryLanguage,

    automaticCaptureMode: state.automaticCaptureMode,

    historyVisibleCount: state.historyVisibleCount,

    bundleExportVersion: state.bundleExportVersion,

    onboardingComplete: state.onboardingComplete,

  };

}


