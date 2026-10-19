import ExpoModulesCore
import UIKit
import AVFoundation

public class DiaryOneVisionModule: Module {
  public func definition() -> ModuleDefinition {
    Name("DiaryOneVision")

    Constant("isAvailable") { true }

    AsyncFunction("extractVideoWindowFrames") { (videoUri: String, timestampsMs: [Double], destDir: String, bounds: [Double]) -> [[String: Any]] in
      guard bounds.count == 2, timestampsMs.count > 0, timestampsMs.count <= 12 else {
        throw Self.err(7, "Invalid video frame request")
      }
      let source = try Self.fileURL(from: videoUri)
      let destination = try Self.fileURL(from: destDir)
      try FileManager.default.createDirectory(at: destination, withIntermediateDirectories: true)
      let asset = AVURLAsset(url: source)
      let times = try VideoFrameTimeline.presentationTimes(asset: asset, bounds: (bounds[0], bounds[1]))
      let generator = AVAssetImageGenerator(asset: asset)
      generator.appliesPreferredTrackTransform = true
      generator.requestedTimeToleranceBefore = .zero
      generator.requestedTimeToleranceAfter = .zero
      generator.maximumSize = CGSize(width: 1280, height: 1280)
      var rows: [[String: Any]] = []
      for (index, requested) in timestampsMs.enumerated() {
        let selected = try VideoFrameTimeline.nearest(requested, in: times, startMs: bounds[0], endMs: bounds[1])
        var actual = CMTime.invalid
        let cgImage: CGImage
        do { cgImage = try generator.copyCGImage(at: selected, actualTime: &actual) }
        catch { throw Self.err(8, "Cannot decode video at \(selected.seconds * 1000) ms: \((error as NSError).localizedDescription)") }
        let pts = actual.seconds * 1000
        guard pts.isFinite, pts.rounded() >= bounds[0], pts.rounded() < bounds[1],
              abs(pts - selected.seconds * 1000) < 0.5 else {
          throw Self.err(9, "Video decoder returned an unexpected presentation timestamp")
        }
        guard let jpeg = UIImage(cgImage: cgImage).jpegData(compressionQuality: 0.85) else {
          throw Self.err(4, "jpeg encode failed")
        }
        let file = destination.appendingPathComponent(String(format: "vframe_%03d_%d.jpg", index, Int(requested.rounded())))
        try jpeg.write(to: file, options: .atomic)
        rows.append(["uri": file.absoluteString, "requestedMs": requested,
                     "actualPtsMs": pts, "decodeTimeMs": selected.seconds * 1000])
      }
      return rows
    }

    AsyncFunction("normalizeEvidenceFrame") { (sourceUri: String, destUri: String) in
      let source = try Self.fileURL(from: sourceUri)
      let destination = try Self.fileURL(from: destUri)
      guard let image = UIImage(contentsOfFile: source.path), image.size.width > 0, image.size.height > 0 else {
        throw Self.err(5, "cannot read selected video frame")
      }
      let size = CGSize(width: 768, height: 1024)
      let scale = min(size.width / image.size.width, size.height / image.size.height)
      let fitted = CGSize(width: image.size.width * scale, height: image.size.height * scale)
      let format = UIGraphicsImageRendererFormat()
      format.scale = 1
      format.opaque = true
      let renderer = UIGraphicsImageRenderer(size: size, format: format)
      let output = renderer.image { context in
        UIColor.black.setFill()
        context.fill(CGRect(origin: .zero, size: size))
        image.draw(in: CGRect(x: (size.width - fitted.width) / 2, y: (size.height - fitted.height) / 2,
                              width: fitted.width, height: fitted.height))
      }
      guard let jpeg = output.jpegData(compressionQuality: 0.84) else {
        throw Self.err(6, "cannot encode normalized evidence frame")
      }
      try jpeg.write(to: destination, options: .atomic)
    }

    AsyncFunction("extractVideoFrames") { (videoUri: String, timestampsMs: [Double], destDir: String) -> [[String: Any]] in
      let videoURL = try Self.fileURL(from: videoUri)
      let destURL = try Self.fileURL(from: destDir)
      try FileManager.default.createDirectory(at: destURL, withIntermediateDirectories: true)

      let asset = AVURLAsset(url: videoURL)
      let generator = AVAssetImageGenerator(asset: asset)
      generator.appliesPreferredTrackTransform = true
      generator.requestedTimeToleranceBefore = .zero
      generator.requestedTimeToleranceAfter = .zero
      generator.maximumSize = CGSize(width: 1280, height: 1280)

      var rows: [[String: Any]] = []
      for (index, requested) in timestampsMs.enumerated() {
        let ms = max(0, requested)
        let time = CMTime(seconds: ms / 1000.0, preferredTimescale: 600)
        var actual = CMTime.zero
        let cgImage = try generator.copyCGImage(at: time, actualTime: &actual)
        let image = UIImage(cgImage: cgImage)
        guard let jpeg = image.jpegData(compressionQuality: 0.85) else {
          throw Self.err(4, "jpeg encode failed")
        }
        let name = String(format: "vframe_%03d_%d.jpg", index, Int(ms.rounded()))
        let out = destURL.appendingPathComponent(name)
        try jpeg.write(to: out, options: .atomic)
        rows.append([
          "uri": out.absoluteString,
          "requestedMs": ms,
          "actualPtsMs": actual.seconds * 1000.0,
        ])
      }
      return rows
    }
  }

  private static func err(_ code: Int, _ message: String) -> NSError {
    NSError(domain: "DiaryOneVision", code: code, userInfo: [NSLocalizedDescriptionKey: message])
  }

  private static func fileURL(from uri: String) throws -> URL {
    if uri.hasPrefix("file://"), let url = URL(string: uri) {
      return url
    }
    if uri.hasPrefix("/") {
      return URL(fileURLWithPath: uri)
    }
    if let url = URL(string: uri), url.isFileURL {
      return url
    }
    throw err(1, "file uri required")
  }

}
