/** Back-compat re-exports — default pipeline uses V04 via buildAppLibraryBundle. */
export type { AppLibraryBundle, BundleExportVersion } from './bundleTypes';
export { buildAppLibraryBundle, buildBundleV03 } from './buildAppLibraryBundle';
