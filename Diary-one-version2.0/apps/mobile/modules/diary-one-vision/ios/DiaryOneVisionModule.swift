import ExpoModulesCore
import Vision
import UIKit
import AVFoundation

public class DiaryOneVisionModule: Module {
  public func definition() -> ModuleDefinition {
    Name("DiaryOneVision")

    Constant("isAvailable") { true }

    AsyncFunction("analyzeImages") { (uris: [String]) -> [String: Any] in
      let modelId = "APPLE_VISION_FEATURE_PRINT_REVISION_\(VNGenerateImageFeaturePrintRequestRevision2)"
      var vectors: [[Double]] = []
      var classifications: [[[String: Any]]] = []

      for uri in uris {
        let uiImage = try Self.loadUIImage(uri: uri)
        guard let cgImage = uiImage.cgImage else {
          throw Self.err(2, "cannot load image")
        }
        let orientation = Self.cgOrientation(uiImage.imageOrientation)

        let featureRequest = VNGenerateImageFeaturePrintRequest()
        featureRequest.revision = VNGenerateImageFeaturePrintRequestRevision2
        let classifyRequest = VNClassifyImageRequest()
        let handler = VNImageRequestHandler(cgImage: cgImage, orientation: orientation, options: [:])
        try handler.perform([featureRequest, classifyRequest])

        guard let observation = featureRequest.results?.first as? VNFeaturePrintObservation,
              observation.elementType == .float else {
          throw Self.err(3, "missing feature print")
        }
        let count = observation.elementCount
        var vector: [Double] = []
        vector.reserveCapacity(Int(count))
        observation.data.withUnsafeBytes { raw in
          let floats = raw.bindMemory(to: Float.self)
          for i in 0..<Int(count) {
            vector.append(Double(floats[i]))
          }
        }
        vectors.append(vector)

        var labels: [[String: Any]] = []
        if let results = classifyRequest.results {
          let limit = min(10, results.count)
          for i in 0..<limit {
            let item = results[i]
            labels.append([
              "identifier": item.identifier,
              "confidence": item.confidence,
            ])
          }
        }
        classifications.append(labels)
      }

      return [
        "modelId": modelId,
        "vectors": vectors,
        "classifications": classifications,
      ]
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

  private static func loadUIImage(uri: String) throws -> UIImage {
    let url = try fileURL(from: uri)
    guard let image = UIImage(contentsOfFile: url.path) else {
      throw err(2, "cannot load image")
    }
    return image
  }

  private static func cgOrientation(_ o: UIImage.Orientation) -> CGImagePropertyOrientation {
    switch o {
    case .up: return .up
    case .down: return .down
    case .left: return .left
    case .right: return .right
    case .upMirrored: return .upMirrored
    case .downMirrored: return .downMirrored
    case .leftMirrored: return .leftMirrored
    case .rightMirrored: return .rightMirrored
    @unknown default: return .up
    }
  }
}
