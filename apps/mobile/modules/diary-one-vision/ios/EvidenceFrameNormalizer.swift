import Foundation
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

/// Encodes the evidence contract from decoded pixels, without copying source EXIF/GPS.
enum EvidenceFrameNormalizer {
  static let width = 768
  static let height = 1024

  private static func fail(_ message: String) -> NSError {
    NSError(domain: "DiaryOneEvidence", code: 1,
            userInfo: [NSLocalizedDescriptionKey: "EVIDENCE_IMAGE_INVALID: " + message])
  }

  // ImageIO may decode a truncated JPEG and still report statusComplete. Walk the
  // marker stream so an EOI inside an EXIF thumbnail cannot hide a missing image tail.
  private static func completeJPEG(_ data: Data) -> Bool {
    guard data.count >= 4, data[0] == 0xff, data[1] == 0xd8 else { return false }
    var i = 2
    while i < data.count {
      guard data[i] == 0xff else { return false }
      while i < data.count, data[i] == 0xff { i += 1 }
      guard i < data.count else { return false }
      let marker = data[i]; i += 1
      if marker == 0xd9 { return true }
      if marker == 0x01 || (0xd0...0xd7).contains(marker) { continue }
      guard marker != 0x00, marker != 0xd8, i + 1 < data.count else { return false }
      let length = Int(data[i]) * 256 + Int(data[i + 1])
      guard length >= 2, length <= data.count - i else { return false }
      i += length
      if marker == 0xda {
        while i < data.count {
          if data[i] != 0xff { i += 1; continue }
          let start = i
          while i < data.count, data[i] == 0xff { i += 1 }
          guard i < data.count else { return false }
          if data[i] == 0x00 || (0xd0...0xd7).contains(data[i]) { i += 1; continue }
          i = start
          break
        }
      }
    }
    return false
  }

  static func normalize(source: URL, destination: URL,
                        spatial: String = "ASPECT_FIT_LETTERBOX") throws -> [String: Any] {
    try autoreleasepool {
      guard source.standardizedFileURL != destination.standardizedFileURL,
            ["ASPECT_FIT_LETTERBOX", "CENTER_CROP_ASPECT_FILL"].contains(spatial) else {
        throw fail("invalid normalization request")
      }
      guard let input = CGImageSourceCreateWithURL(source as CFURL,
              [kCGImageSourceShouldCache: false] as CFDictionary),
            CGImageSourceGetCount(input) > 0 else { throw fail("cannot read selected image") }
      if CGImageSourceGetType(input) as String? == UTType.jpeg.identifier,
         !completeJPEG(try Data(contentsOf: source, options: .mappedIfSafe)) {
        throw fail("incomplete selected JPEG")
      }
      guard let decoded = CGImageSourceCreateThumbnailAtIndex(input, 0, [
              kCGImageSourceCreateThumbnailFromImageAlways: true,
              kCGImageSourceCreateThumbnailWithTransform: true,
              kCGImageSourceThumbnailMaxPixelSize: 2048,
              kCGImageSourceShouldCacheImmediately: true,
            ] as CFDictionary),
            CGImageSourceGetStatusAtIndex(input, 0) == .statusComplete else {
        throw fail("cannot decode selected image")
      }
      // An explicit 8-bit sRGB canvas avoids device-scale and HDR container differences.
      guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB),
            let canvas = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8,
              bytesPerRow: width * 4, space: colorSpace,
              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else {
        throw fail("cannot create evidence canvas")
      }
      let target = CGSize(width: width, height: height)
      let ratios = (target.width / CGFloat(decoded.width), target.height / CGFloat(decoded.height))
      let scale = spatial == "ASPECT_FIT_LETTERBOX" ? min(ratios.0, ratios.1) : max(ratios.0, ratios.1)
      let fitted = CGSize(width: CGFloat(decoded.width) * scale, height: CGFloat(decoded.height) * scale)
      canvas.setFillColor(CGColor(gray: 0, alpha: 1))
      canvas.fill(CGRect(origin: .zero, size: target))
      canvas.interpolationQuality = .high
      canvas.draw(decoded, in: CGRect(x: (target.width - fitted.width) / 2,
        y: (target.height - fitted.height) / 2, width: fitted.width, height: fitted.height))
      guard let image = canvas.makeImage() else { throw fail("cannot render evidence") }
      let bytes = NSMutableData()
      guard let encoder = CGImageDestinationCreateWithData(bytes, UTType.jpeg.identifier as CFString, 1, nil) else {
        throw fail("cannot create JPEG encoder")
      }
      CGImageDestinationAddImage(encoder, image, [kCGImageDestinationLossyCompressionQuality: 0.84] as CFDictionary)
      guard CGImageDestinationFinalize(encoder) else { throw fail("cannot encode evidence JPEG") }
      try (bytes as Data).write(to: destination, options: .atomic)
      do {
        // Read the saved file, not the input's metadata or intended canvas dimensions.
        guard let saved = CGImageSourceCreateWithURL(destination as CFURL, nil),
              CGImageSourceGetType(saved) as String? == UTType.jpeg.identifier,
              CGImageSourceGetCount(saved) == 1,
              let pixels = CGImageSourceCreateImageAtIndex(saved, 0, nil),
              CGImageSourceGetStatusAtIndex(saved, 0) == .statusComplete,
              pixels.width == width, pixels.height == height else {
          throw fail("encoded format or dimensions mismatch")
        }
        return ["uri": destination.absoluteString, "width": pixels.width, "height": pixels.height,
                "format": "JPEG", "spatialTransform": spatial]
      } catch {
        try? FileManager.default.removeItem(at: destination)
        throw error
      }
    }
  }
}
