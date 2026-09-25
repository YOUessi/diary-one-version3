import * as Sharing from 'expo-sharing';
import * as MediaLibrary from 'expo-media-library/legacy';

export async function shareImageUri(uri: string): Promise<void> {
  const available = await Sharing.isAvailableAsync();
  if (!available) throw new Error('Sharing is not available on this device.');
  await Sharing.shareAsync(uri, { mimeType: 'image/jpeg', dialogTitle: 'Share memory' });
}

export async function saveImageToPhotos(uri: string): Promise<void> {
  const perm = await MediaLibrary.requestPermissionsAsync();
  if (!perm.granted) throw new Error('Photos permission is required to save.');
  await MediaLibrary.saveToLibraryAsync(uri);
}
