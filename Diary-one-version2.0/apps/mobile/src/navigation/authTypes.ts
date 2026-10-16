/**
 * Shared auth screens mounted on both OnboardingStack and AccountStack.
 * Keep SignIn / EmailOtp param shapes identical across stacks.
 */
export type AuthFlowParams = {
  SignIn: { mode?: 'account' } | undefined;
  EmailOtp: { email: string; mode?: 'account' };
};
