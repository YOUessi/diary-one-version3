export type BundleExportVersion = 'V03' | 'V04';

export type SpatialTransform = 'CENTER_CROP_ASPECT_FILL' | 'ASPECT_FIT_LETTERBOX';

export const BUNDLE_VERSION_ID: Record<BundleExportVersion, string> = {
  V03: 'DIARY_ONE_APP_LIBRARY_BUNDLE_V03',
  V04: 'DIARY_ONE_APP_LIBRARY_BUNDLE_V04',
};

export function spatialTransformFor(version: BundleExportVersion): SpatialTransform {
  return version === 'V04' ? 'ASPECT_FIT_LETTERBOX' : 'CENTER_CROP_ASPECT_FILL';
}

export type AppLibraryBundle = {
  bundle_version: string;
  research_only: true;
  session: { session_id: string; exported_at: string; timezone: string };
  device: {
    device_id: string;
    hardware_revision: string;
    firmware_version: string;
    sdk_version: string;
  };
  normalization: {
    width: 768;
    height: 1024;
    orientation: 'PORTRAIT';
    aspect_ratio: '3:4';
    spatial_transform: SpatialTransform;
    temporal_transform: 'PHONE_TEST_DURATION_WINDOWS_V01';
    canonical_frame_offsets_ms: [1500, 4500, 7500];
    evidence_profile_version: 'PHONE_TEST_DURATION_WINDOWS_V01';
  };
  assets: Record<string, unknown>[];
};
