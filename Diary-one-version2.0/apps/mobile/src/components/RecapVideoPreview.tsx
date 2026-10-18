import React from 'react';
import { VideoPlayback } from './VideoPlayback';

/** Recaps follow the same explicit-play and interruption rules as other videos. */
export function RecapVideoPreview({ videoUri, posterUri }: { videoUri: string; posterUri: string }) {
  return <VideoPlayback uri={videoUri} posterUri={posterUri} initialMuted />;
}
