// Diary One — domain model (internal: Chapter / Aha; UI: memory / small memory)

export type TodayStatus =
  | 'UNSYNCED'
  | 'PREPARING'
  | 'READY'
  | 'READY_NEW_RECORDINGS'
  | 'READY_PREPARING'
  | 'ZERO_CURATED'
  | 'NO_RECORDINGS'
  | 'PARTIAL';

/** Optional local ordering evidence; old saved memories may have neither. */
export type MemoryOrder = { capturedAtMs?: number; sourceSequenceIndex?: number };

export type MemoryMedia = {
  id: string;
  label: string;
  capturedByYou?: boolean;
  posterUri?: string;
  playbackUri?: string;
  /** Seek into the original video, not a claim that a short clip was exported. */
  focusTimeSec?: number;
};

export type Chapter = MemoryOrder & {
  id: string;
  /** Local ingestion provenance, not an AI/public payload field. */
  sourceBatchId?: string;
  yourStoryRevision?: number;
  title: string;
  dateKey: string;
  dateLabel: string;
  weakTime?: string;
  aiStory: string;
  previewStory?: string;
  highlights?: { id: string; text: string; media?: MemoryMedia[] }[];
  tags: string[];
  detailTags?: string[];
  heroUri?: string;
  moments: MemoryMedia[];
  yourStory?: string;
};

export type SmallMemory = MemoryOrder & {
  id: string;
  sourceBatchId?: string;
  text: string;
  posterUri?: string;
};

/** Soft topic facet for Memory · Your Topics (人 / 事 / 地 / other). */
export type TopicFacet = 'person' | 'event' | 'place' | 'other';

export type Topic = {
  id: string;
  name: string;
  chapterIds: string[];
  /** Heuristic from tag vocabulary — not a hard cloud ontology. */
  facet?: TopicFacet;
};

export type MemoryPreference = {
  id: string;
  title: string;
  text: string;
  /** Questionnaire provenance and scope, separate from captured-content tags. */
  survey?: {
    source: 'preference_survey';
    polarity: 'like' | 'avoid';
    theme_id?: string;
    tag_id?: string;
    preference_reason_id?: string;
    target_scope: string;
    strength: number;
    updated_at: string;
  };
};

export type PreferenceSurveyResponse = {
  question_1_response: 'selected' | 'no_preference' | 'skipped';
  question_2_response: 'selected' | 'nothing_for_now' | 'skipped';
  updated_at: string;
};

export type CapturedOriginal = {
  id: string;
  /** Only trusted device Manual capture may appear in Captured by You. */
  intakeSource?: 'DEVICE_MANUAL' | import('./domain/mediaIntake').MediaIntakeSource;
  dateKey: string;
  kind: 'photo' | 'video';
  durationSec?: number;
  posterUri?: string;
  playbackUri?: string;
  /** Viewer subtitle e.g. Aug 16, 2026 · 8:31 AM */
  capturedAtLabel?: string;
};

export const seedChapters: Chapter[] = [
  {
    id: 'ch-morning-fishing',
    title: 'Morning Fishing',
    dateKey: '2026-08-16',
    dateLabel: 'Sat, Aug 16',
    weakTime: 'Morning',
    aiStory: 'A quiet morning beside the lake.',
    tags: ['Fishing', 'Outdoors'],
    detailTags: ['Lakeside', 'Weekend', 'Quiet morning'],
    yourStory:
      'I almost went home early, but staying for another half hour made the morning feel completely different.',
    /** Seed stills for Expo Go Share (collage / illustrated / recap) without import. */
    heroUri: 'https://picsum.photos/seed/diary-fish/1080/1350',
    moments: [
      {
        id: 'm1',
        label: '7:42 AM',
        posterUri: 'https://picsum.photos/seed/diary-fish-m1/800/1000',
      },
      {
        id: 'm2',
        label: '8:06 AM · Motion',
        posterUri: 'https://picsum.photos/seed/diary-fish-m2/800/1000',
        playbackUri:
          'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
      },
      {
        id: 'm3',
        label: '8:31 AM · 4s short clip',
        capturedByYou: true,
        posterUri: 'https://picsum.photos/seed/diary-fish-m3/800/1000',
        playbackUri:
          'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
      },
    ],
  },
  {
    id: 'ch-afternoon-citywalk',
    title: 'Afternoon Citywalk',
    dateKey: '2026-08-16',
    dateLabel: 'Sat, Aug 16',
    weakTime: 'Afternoon',
    aiStory: 'The city slowed down for a walk with no destination.',
    tags: ['Citywalk', 'Dog walk'],
    heroUri: 'https://picsum.photos/seed/diary-city/1080/1350',
    moments: [
      {
        id: 'm-city-1',
        label: '3:12 PM',
        posterUri: 'https://picsum.photos/seed/diary-city-m1/800/1000',
      },
    ],
  },
  {
    id: 'ch-dinner-friends',
    title: 'Dinner with Friends',
    dateKey: '2026-08-15',
    dateLabel: 'Fri, Aug 15',
    weakTime: 'Evening',
    aiStory: 'Dinner ran long, and nobody seemed in a hurry to leave.',
    tags: ['Friends', 'Dinner'],
    heroUri: 'https://picsum.photos/seed/diary-dinner/1080/1350',
    moments: [
      {
        id: 'm-dinner-1',
        label: '7:45 PM',
        posterUri: 'https://picsum.photos/seed/diary-dinner-m1/800/1000',
      },
    ],
  },
  {
    id: 'ch-studio-morning',
    title: 'A Slow Studio Morning',
    dateKey: '2026-08-14',
    dateLabel: 'Thu, Aug 14',
    weakTime: 'Morning',
    aiStory: 'Coffee, sketches, and an unhurried start to the day.',
    tags: ['Studio', 'Coffee'],
    heroUri: 'https://picsum.photos/seed/diary-studio/1080/1350',
    moments: [
      {
        id: 'm-studio-1',
        label: '9:10 AM',
        posterUri: 'https://picsum.photos/seed/diary-studio-m1/800/1000',
      },
    ],
  },
  {
    id: 'ch-fishing-before-rain',
    title: 'Before the rain came in',
    dateKey: '2026-07-28',
    dateLabel: 'Mon, Jul 28',
    weakTime: 'Afternoon',
    aiStory: 'Packed up just as the wind picked up.',
    tags: ['Fishing', 'Weekend'],
    heroUri: 'https://picsum.photos/seed/diary-rain/1080/1350',
    moments: [
      {
        id: 'm-rain-1',
        label: '4:12 PM',
        posterUri: 'https://picsum.photos/seed/diary-rain-m1/800/1000',
      },
    ],
  },
  {
    id: 'ch-fishing-river-calm',
    title: 'A calm hour by the river',
    dateKey: '2026-07-09',
    dateLabel: 'Wed, Jul 9',
    weakTime: 'Morning',
    aiStory: 'Nothing much happened, which was exactly the point.',
    tags: ['Fishing', 'Solo'],
    heroUri: 'https://picsum.photos/seed/diary-river/1080/1350',
    moments: [
      {
        id: 'm-river-1',
        label: '8:05 AM',
        posterUri: 'https://picsum.photos/seed/diary-river-m1/800/1000',
      },
    ],
  },
  {
    id: 'ch-late-afternoon-water',
    title: 'Late afternoon by the water',
    dateKey: '2026-08-03',
    dateLabel: 'Mon, Aug 3',
    weakTime: 'Afternoon',
    aiStory: 'Stayed by the water until the light softened.',
    tags: ['Lakeside', 'Weekend'],
    heroUri: 'https://picsum.photos/seed/diary-water/1080/1350',
    moments: [
      {
        id: 'm-water-1',
        label: '5:40 PM',
        posterUri: 'https://picsum.photos/seed/diary-water-m1/800/1000',
      },
    ],
  },
];

export const seedSmallMemories: Record<string, SmallMemory[]> = {
  '2026-08-16': [{ id: 's1', text: 'A brief rainbow caught the wet pavement.' }],
  '2026-08-15': [],
};

export const seedTopics: Topic[] = [
  {
    id: 't1',
    name: 'Fishing',
    chapterIds: [
      'ch-morning-fishing',
      'ch-fishing-before-rain',
      'ch-fishing-river-calm',
      'ch-late-afternoon-water',
    ],
  },
  { id: 't2', name: 'Running', chapterIds: [] },
  { id: 't3', name: 'Model Building', chapterIds: [] },
  { id: 't4', name: 'Coffee', chapterIds: ['ch-studio-morning'] },
  { id: 't5', name: 'Architecture', chapterIds: [] },
  { id: 't6', name: 'City Walk', chapterIds: ['ch-afternoon-citywalk'] },
];

export const seedPreferences: MemoryPreference[] = [
  {
    id: 'p1',
    title: 'Fishing',
    text: 'Quiet mornings by the water and time spent outdoors fishing.',
  },
  {
    id: 'p2',
    title: 'Model Building',
    text: 'Keep the progress, details, and finished stages of my model projects.',
  },
  {
    id: 'p3',
    title: 'Food',
    text: 'Meals, restaurants, and food moments are worth remembering.',
  },
  {
    id: 'p4',
    title: 'Family',
    text: 'Time with my family matters, even when nothing special is planned.',
  },
  {
    id: 'p5',
    title: 'Running',
    text: 'Runs, routes, and how movement shapes the day.',
  },
  {
    id: 'p6',
    title: 'Coffee',
    text: 'Slow café mornings and the rituals around a good cup.',
  },
];

function seedCapturedBatch(): CapturedOriginal[] {
  const items: CapturedOriginal[] = [];
  for (let i = 0; i < 12; i++) {
    const seed = `diary-cap-photo-${i}`;
    const posterUri = `https://picsum.photos/seed/${seed}/800/1000`;
    items.push({
      id: `cap-photo-${i}`,
      dateKey: i < 8 ? '2026-08-16' : '2026-08-15',
      kind: 'photo',
      capturedAtLabel: i < 8 ? 'Aug 16, 2026 · 8:31 AM' : 'Aug 15, 2026 · 6:02 PM',
      posterUri,
      playbackUri: posterUri,
    });
  }
  const sampleMp4 =
    'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4';
  for (let i = 0; i < 3; i++) {
    const seed = `diary-cap-video-${i}`;
    const posterUri = `https://picsum.photos/seed/${seed}/800/1000`;
    items.push({
      id: `cap-video-${i}`,
      dateKey: i === 0 ? '2026-08-16' : '2026-08-15',
      kind: 'video',
      durationSec: i === 0 ? 15 : 60,
      capturedAtLabel: i === 0 ? 'Aug 16, 2026 · 8:31 AM' : 'Aug 15, 2026 · 7:10 PM',
      posterUri,
      playbackUri: sampleMp4,
    });
  }
  return items;
}

export const seedCaptured: CapturedOriginal[] = seedCapturedBatch();

/** Days that have published chapter or small memory (calendar dots). */
export function daysWithContent(chapters: Chapter[], smallByDate: Record<string, SmallMemory[]>) {
  const keys = new Set<string>();
  chapters.forEach((c) => keys.add(c.dateKey));
  Object.entries(smallByDate).forEach(([k, v]) => {
    if (v.length) keys.add(k);
  });
  return keys;
}
