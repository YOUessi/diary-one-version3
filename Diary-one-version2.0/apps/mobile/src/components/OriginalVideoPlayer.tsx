import React from 'react';
import { VideoPlayback } from './VideoPlayback';

export function OriginalVideoPlayer({ uri, durationSec }: { uri: string; durationSec?: number }) {
  return <VideoPlayback uri={uri} durationSec={durationSec} immersive />;
}
