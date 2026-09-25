export type LocalProfile = {
  nickname: string;
  email?: string;
  avatarUri?: string;
};

export const DEFAULT_LOCAL_PROFILE: LocalProfile = {
  nickname: 'Gordon',
  email: 'gordon@example.com',
};
