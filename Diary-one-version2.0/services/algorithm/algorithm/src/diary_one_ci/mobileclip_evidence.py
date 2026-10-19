"""Explicit V04 sampling extension; preserve actual v07 frame counts and PTS."""
PROFILE = 'MOBILECLIP_S0_FP16_COVERAGE_V07'
BALANCED_PROFILE = 'MOBILECLIP_S0_FP16_COVERAGE_V07_BALANCED_V1'
REPLAY_PROFILE = 'OFFLINE_MOBILECLIP_S0_FP16_V07_REPLAY'


def validate_mobileclip_frames(asset):
    duration = asset['original_duration_ms']
    if type(duration) is not int or not 0 < duration <= 120_000:
        raise ValueError('MobileCLIP video duration must be 1..120000 ms')
    replay = asset.get('evidence_sampling_profile') == REPLAY_PROFILE
    # Offline Mac experiments sampled each supplied clip as one unit. Their
    # actual container durations can exceed 10 s by a few milliseconds. Preserve
    # the original PTS/counts explicitly; never pad them into the phone profile.
    if replay and duration > 11000:
        raise ValueError('Offline replay accepts existing ~10-second clips only')
    windows = 1 if replay else (duration + 9999) // 10000
    if type(asset['evidence_window_count']) is not int or asset['evidence_window_count'] != windows:
        raise ValueError('MobileCLIP window count mismatch')
    frames = asset['frames']
    timestamps = [f['source_timestamp_ms'] for f in frames]
    if any(type(t) is not int for t in timestamps) or timestamps != sorted(set(timestamps)):
        raise ValueError('MobileCLIP anchors must be unique chronological integer PTS')
    for f in frames:
        if type(f['window_index']) is not int or not 0 <= f['window_index'] < windows:
            raise ValueError('MobileCLIP window index out of range')
        if type(f['window_count']) is not int or f['window_count'] != windows:
            raise ValueError('MobileCLIP frame window count mismatch')
        balanced = asset.get('evidence_sampling_profile') == BALANCED_PROFILE
        start = f['window_index'] * duration // windows if balanced else f['window_index'] * 10000
        end = ((f['window_index'] + 1) * duration // windows if balanced
               else duration if replay else min(duration, start + 10000))
        if not start <= f['source_timestamp_ms'] < end:
            raise ValueError('MobileCLIP anchor is outside its window')
    for window in range(windows):
        group = [f for f in frames if f['window_index'] == window]
        # V07 adjusts 1..5 candidates; an original FIXED_10 is preserved.
        if not 1 <= len(group) <= 10:
            raise ValueError('MobileCLIP requires 1..10 real frames in every window')
        for i, frame in enumerate(group):
            ratio = i / (len(group) - 1) if len(group) > 1 else 0.5
            role, offset = ('WINDOW_EARLY', 1500) if ratio <= 0.34 else ('WINDOW_LATE', 7500) if ratio >= 0.66 else ('WINDOW_MIDDLE', 4500)
            if frame['sample_role'] != role or frame['canonical_offset_ms'] != offset:
                raise ValueError('MobileCLIP role/offset mismatch')
