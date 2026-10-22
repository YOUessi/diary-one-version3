export type OnboardingStackParamList = {
  /** mode=account: OTP then return to Account (no pairing). */
  SignIn: { mode?: 'account' } | undefined;
  EmailOtp: { email: string; mode?: 'account' };
  PairingStart: undefined;
  PairingBluetoothPermission: undefined;
  PairingBluetoothDenied: undefined;
  PairingSearching: undefined;
  PairingFound: undefined;
  PairingConnecting: undefined;
  PairingConnected: undefined;
  PermissionBluetoothRequest: undefined;
  PermissionBluetoothDenied: undefined;
  PermissionLocalNetworkRequest: undefined;
  PermissionLocalNetworkDenied: undefined;
  PermissionPhotosRequest: undefined;
  PermissionPhotosDenied: undefined;
  PermissionNotificationsRequest: undefined;
  PermissionNotificationsDenied: undefined;
  SetupComplete: undefined;
  HardwareBasics: { step: number };
  /** Meeting 2026-09-23 light preference survey (skippable). */
  PreferenceSurvey: {
    step?: number | string;
    mode?: 'onboarding' | 'account';
    answers?: import('../onboarding/preferenceSurvey').SurveyAnswers;
  };
};

export type DiaryStackParamList = {
  DiaryHome: undefined;
  CalendarExpanded: undefined;
  ChapterDetail: { chapterId: string };
  Search: { initialQuery?: string };
  ShareMemorySelector: { chapterId: string };
  ShareDaySelector: { dateKey: string };
  DayPhotoCollageFlow: { dateKey: string; phase: 'preparing' | 'preview' | 'failed'; previewUri?: string };
  YourStoryRemoveConfirm: { chapterId: string };
  YourStoryRemoveFailed: { chapterId: string };
  PhotoCollageFlow: { chapterId: string; phase: 'preparing' | 'preview' | 'failed'; previewUri?: string };
  IllustratedShareFlow: {
    chapterId: string;
    phase: 'picker' | 'preparing' | 'preview' | 'failed';
    style?: 'A' | 'B' | 'C';
    previewUri?: string;
  };
  DailyRecapFlow: {
    dateKey: string;
    phase: 'preparing' | 'preview' | 'failed' | 'readiness_changed';
    errorHint?: string;
    asset?: import('../share/buildDailyRecap').DailyRecapAsset;
  };
};

export type MemoryStackParamList = Pick<DiaryStackParamList,
  'ChapterDetail' | 'ShareMemorySelector' | 'YourStoryRemoveConfirm' |
  'YourStoryRemoveFailed' | 'PhotoCollageFlow' | 'IllustratedShareFlow'> & {
  MemoryHome: undefined;
  Search: { initialQuery?: string };
  CapturedByYou: { filter?: 'all' | 'photo' | 'video' } | undefined;
  TopicsList: undefined;
  TopicDetail: { topicId: string };
  OriginalViewer: { captureId: string };
  OriginalDeleteConfirm: { captureId: string };
};

export type DeviceStackParamList = {
  DeviceHome: undefined;
  AutomaticCapture: undefined;
  DeviceSettings: undefined;
};

export type AccountStackParamList = {
  AccountHome: undefined;
  MemoryPreferences: undefined;
  PreferenceAdd: undefined;
  PreferenceEdit: { preferenceId: string };
  PreferenceDeleteConfirm: { preferenceId: string };
  PrivacyData: undefined;
  PrivacyDetail: { section: PrivacyDetailSection };
  HelpTopic: { topicId: HelpTopicId };
  EditProfile: undefined;
  Notifications: undefined;
  Language: undefined;
  HelpFeedback: undefined;
  Plan: undefined;
  Licenses: undefined;
  PreferenceSurvey: {
    step?: number | string;
    mode?: 'onboarding' | 'account';
    answers?: import('../onboarding/preferenceSurvey').SurveyAnswers;
  };
  /** Internal beta — OTP without leaving main tabs / replaying hardware onboarding. */
  SignIn: { mode?: 'account' } | undefined;
  EmailOtp: { email: string; mode?: 'account' };
  InternalLab: undefined;
};

export type PrivacyDetailSection =
  | 'stored_memories'
  | 'memory_profile'
  | 'export_data'
  | 'delete_account'
  | 'privacy_policy'
  | 'terms';

export type HelpTopicId =
  | 'pairing'
  | 'sync'
  | 'capture'
  | 'memories'
  | 'battery'
  | 'report'
  | 'feedback'
  | 'device_basics'
  | 'contact';

export type RootTabParamList = {
  DiaryTab: undefined;
  MemoryTab: undefined;
  DeviceTab: undefined;
  AccountTab: undefined;
};
