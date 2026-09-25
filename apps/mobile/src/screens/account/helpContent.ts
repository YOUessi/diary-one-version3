import type { HelpTopicId } from '../../navigation/types';

export const HELP_TOPICS: { id: HelpTopicId; title: string; body: string }[] = [
  {
    id: 'pairing',
    title: 'Pairing & Connection',
    body:
      'Power on Diary One and choose Find Diary One during setup. Bluetooth is requested only when you start pairing. Wi-Fi sync is separate and runs when recordings are ready to transfer.',
  },
  {
    id: 'sync',
    title: 'Sync',
    body:
      'Sync transfers recordings from Diary One to your iPhone. It does not replace cloud processing that turns recordings into curated memories. Use the Device tab when new recordings are ready.',
  },
  {
    id: 'capture',
    title: 'Capture & Camera',
    body:
      'Use the left wheel for Photo, Quick Video, or Long Video. Double tap the touch surface to capture deliberately. The right dial adjusts camera angle; Camera Hidden pauses visual capture.',
  },
  {
    id: 'memories',
    title: 'Memories & Processing',
    body:
      'After sync, processing selects and organizes moments into memories. Your “what you remember” edits are kept separately and never invent facts that are not supported by footage.',
  },
  {
    id: 'battery',
    title: 'Battery & Storage',
    body:
      'Low battery is primarily communicated on Diary One hardware in V1. Storage and last sync appear on the Device tab when a real connection is available — values are not guessed in this build.',
  },
  {
    id: 'device_basics',
    title: 'Device Basics',
    body:
      'Seven short steps cover wearing Diary One, capture controls, automatic capture, and how recordings become memories. The full walkthrough is listed below.',
  },
  {
    id: 'report',
    title: 'Report a Problem',
    body:
      'Reports may include app/iOS version, firmware, device ID, connection/storage state and error logs only with your opt-in. User media and your added memory details are never attached automatically.',
  },
  {
    id: 'feedback',
    title: 'Send Feedback',
    body: 'Share product feedback by email. Include what you expected and what happened so we can reproduce issues.',
  },
  {
    id: 'contact',
    title: 'Contact Support',
    body: 'Email support@diary.one for help with Diary One hardware, sync, or memories.',
  },
];

export function helpTopicById(id: HelpTopicId) {
  return HELP_TOPICS.find((t) => t.id === id);
}
