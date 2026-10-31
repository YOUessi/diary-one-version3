import Foundation
import AVFoundation
import UIKit

/// Converts only final, cloud-selected Chapter pictures into a real three-second
/// silent local movie. Original 10-second footage stays private and unchanged.
///
/// This produces the Chapter *in-app motion asset*. Apple Photos-native paired
/// HEIC/MOV metadata is a separate export boundary and must not be claimed here.
enum ChapterMotionExporter {
  static func export(
    sourceURL: URL, destinationDirectory: URL,
    assetKey: String, focusMs: Double, targetMs: Double,
    completion: @escaping (Result<[String: Any], Error>) -> Void
  ) throws {
    guard sourceURL.isFileURL, destinationDirectory.isFileURL,
          assetKey.range(of: "^[a-zA-Z0-9_-]{1,96}$", options: .regularExpression) != nil,
          focusMs.isFinite, targetMs.isFinite,
          focusMs >= 0, targetMs >= 1000, targetMs <= 5000 else {
      throw NSError(domain:"DiaryOneMotion",code:1,userInfo:[
        NSLocalizedDescriptionKey:"Invalid source, key, or clip duration"])
    }
    let asset=AVURLAsset(url:sourceURL)
    let originalLength=CMTimeGetSeconds(asset.duration)
    guard originalLength.isFinite, originalLength >= targetMs/1000,
          focusMs/1000 < originalLength,
          let originalTrack=asset.tracks(withMediaType:.video).first else {
      throw NSError(domain:"DiaryOneMotion",code:2,userInfo:[
        NSLocalizedDescriptionKey:"Original source video unavailable"])
    }
    let clipLength=targetMs/1000
    let start=max(0,min(focusMs/1000-clipLength/2,originalLength-clipLength))
    let end=start+clipLength
    try FileManager.default.createDirectory(at:destinationDirectory,
        withIntermediateDirectories:true)
    let photo=destinationDirectory.appendingPathComponent(assetKey+".jpg")
    let video=destinationDirectory.appendingPathComponent(assetKey+".mov")
    let info:[String:Any]=[
      "stillUri":photo.absoluteString,"videoUri":video.absoluteString,
      "focusMs":focusMs,"startMs":start*1000,"endMs":end*1000,
      "clipDurationMs":targetMs,"isApplePhotosPaired":false
    ]
    if FileManager.default.fileExists(atPath:photo.path) &&
       FileManager.default.fileExists(atPath:video.path) {
      completion(.success(info))
      return
    }
    if FileManager.default.fileExists(atPath:photo.path) {
      try FileManager.default.removeItem(at:photo)
    }
    if FileManager.default.fileExists(atPath:video.path) {
      try FileManager.default.removeItem(at:video)
    }

    // Still and motion always derive from the SAME original timeline and
    // use the same orientation: no 768×1024 evidence letterbox is exported.
    let generator=AVAssetImageGenerator(asset:asset)
    generator.appliesPreferredTrackTransform=true
    generator.requestedTimeToleranceBefore = .zero
    generator.requestedTimeToleranceAfter = .zero
    let originalTime=CMTime(seconds:focusMs/1000,preferredTimescale:600)
    var actual=CMTime.invalid
    let frame=try generator.copyCGImage(at:originalTime,actualTime:&actual)
    guard abs(actual.seconds-focusMs/1000) <= 0.11,
          let data=UIImage(cgImage:frame).jpegData(compressionQuality:0.92) else {
      throw NSError(domain:"DiaryOneMotion",code:3,userInfo:[
        NSLocalizedDescriptionKey:"Still frame cannot be aligned to source video"])
    }
    try data.write(to:photo,options:.atomic)
    let composition=AVMutableComposition()
    guard let track=composition.addMutableTrack(withMediaType:.video,
        preferredTrackID:kCMPersistentTrackID_Invalid) else {
      throw NSError(domain:"DiaryOneMotion",code:4,userInfo:[
        NSLocalizedDescriptionKey:"Cannot build video-only composition"])
    }
    let range=CMTimeRange(
      start:CMTime(seconds:start,preferredTimescale:600),
      duration:CMTime(seconds:clipLength,preferredTimescale:600))
    try track.insertTimeRange(range,of:originalTrack,at:.zero)
    track.preferredTransform=originalTrack.preferredTransform
    guard let session=AVAssetExportSession(asset:composition,
                                          presetName:AVAssetExportPresetHighestQuality) else {
      throw NSError(domain:"DiaryOneMotion",code:5,userInfo:[
        NSLocalizedDescriptionKey:"Cannot create AVAssetExportSession"])
    }
    guard session.supportedFileTypes.contains(.mov) else {
      throw NSError(domain:"DiaryOneMotion",code:6,userInfo:[
        NSLocalizedDescriptionKey:"MOV export unavailable for this source"])
    }
    session.outputURL=video
    session.outputFileType = .mov
    session.shouldOptimizeForNetworkUse=true
    session.exportAsynchronously {
      if session.status == .completed {
        completion(.success(info))
      } else {
        try? FileManager.default.removeItem(at:video)
        try? FileManager.default.removeItem(at:photo)
        completion(.failure(session.error ?? NSError(
          domain:"DiaryOneMotion",code:7,userInfo:[
            NSLocalizedDescriptionKey:"AVAssetExportSession did not complete"])))
      }
    }
  }
}
