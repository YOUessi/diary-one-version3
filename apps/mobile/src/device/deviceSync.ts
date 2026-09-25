import { performDeviceSyncService } from '../backend/deviceSyncService';

/** 设备→手机同步（不跑云端处理）。未连接时诚实拒绝，不伪造电量/存储。 */
export async function performDeviceSync(): Promise<boolean> {
  const result = await performDeviceSyncService({ showAlerts: true });
  return result.ok;
}
