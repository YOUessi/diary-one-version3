import ExpoModulesCore
import Vision
import UIKit

public class DiaryOneVisionModule: Module {
  public func definition() -> ModuleDefinition {
    Name("DiaryOneVision")

    AsyncFunction("analyzeImages") { (uris: [String]) -> [String: Any] in
      let modelId = "APPLE_VISION_FEATURE_PRINT_REVISION_\(VNGenerateImageFeaturePrintRequestRevision2)"
      var vectors: [[Double]] = []
      var classifications: [[[String: Any]]] = []

      for uri in uris {
        guard let url = URL(string: uri), url.isFileURL else {
          throw NSError(domain: "DiaryOneVision", code: 1, userInfo: [NSLocalizedDescriptionKey: "file uri required"])
        }
        let path = url.path
        guard let uiImage = UIImage(contentsOfFile: path), let cgImage = uiImage.cgImage else {
          throw NSError(domain: "DiaryOneVision", code: 2, userInfo: [NSLocalizedDescriptionKey: "cannot load image"])
        }

        let featureRequest = VNGenerateImageFeaturePrintRequest()
        featureRequest.revision = VNGenerateImageFeaturePrintRequestRevision2
        let classifyRequest = VNClassifyImageRequest()
        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        try handler.perform([featureRequest, classifyRequest])

        guard let observation = featureRequest.results?.first as? VNFeaturePrintObservation,
              observation.elementType == .float else {
          throw NSError(domain: "DiaryOneVision", code: 3, userInfo: [NSLocalizedDescriptionKey: "missing feature print"])
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
  }
}
