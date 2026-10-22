import Foundation
import ImageIO
import UniformTypeIdentifiers

// Test executable only: compile together with the production EvidenceFrameNormalizer.swift.
@main
struct EvidenceImageCheck {
  static func main() throws {
    let data = try Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1]))
    let rows = try JSONSerialization.jsonObject(with: data) as! [[String: String]]
    var results: [[String: Any]] = []
    for row in rows {
      do {
        let source = URL(fileURLWithPath: row["source"]!)
        if let seed = row["heicSeed"] {
          let input = CGImageSourceCreateWithURL(URL(fileURLWithPath: seed) as CFURL, nil)!
          let pixels = CGImageSourceCreateImageAtIndex(input, 0, nil)!
          guard let encoder = CGImageDestinationCreateWithURL(source as CFURL, UTType.heic.identifier as CFString, 1, nil) else {
            throw NSError(domain: "HEIC fixture encoding unavailable", code: 1)
          }
          CGImageDestinationAddImage(encoder, pixels, nil)
          guard CGImageDestinationFinalize(encoder) else { throw NSError(domain: "HEIC fixture failed", code: 1) }
        }
        var result = try EvidenceFrameNormalizer.normalize(source: source,
          destination: URL(fileURLWithPath: row["destination"]!), spatial: row["spatial"]!)
        result["name"] = row["name"]!
        result["ok"] = true
        results.append(result)
      } catch {
        results.append(["name": row["name"]!, "ok": false, "error": error.localizedDescription])
      }
    }
    try JSONSerialization.data(withJSONObject: results, options: [.prettyPrinted, .sortedKeys])
      .write(to: URL(fileURLWithPath: CommandLine.arguments[2]))
  }
}
