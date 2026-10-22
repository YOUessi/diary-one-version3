import type { Chapter } from '../model';

/** A cover can play only the original paired with that exact displayed frame. */
export function chapterSlides(chapter: Pick<Chapter, 'heroUri' | 'moments'>) {
  const moments = chapter.moments.filter((m) => m.posterUri || m.playbackUri);
  const heroUri = chapter.heroUri ?? moments[0]?.posterUri;
  const matches = heroUri ? moments.filter((m) => m.posterUri === heroUri) : [];
  const sources = new Set(matches.map((m) => m.playbackUri));
  const hero = matches[0];
  const slides = [
    ...(heroUri ? [{
      key: 'hero',
      posterUri: heroUri,
      playbackUri: sources.size === 1 ? hero?.playbackUri : undefined,
      title: sources.size === 1 ? hero?.label : undefined,
    }] : []),
    ...moments.map((m) => ({
      key: m.id,
      posterUri: m.posterUri ?? m.playbackUri,
      playbackUri: m.playbackUri,
      title: m.label,
    })),
  ];
  return slides.filter((slide, index) =>
    slides.findIndex((other) => other.posterUri === slide.posterUri) === index);
}
