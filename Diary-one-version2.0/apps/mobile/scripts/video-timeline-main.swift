// macOS regression adapter. Compiled with the actual app VideoFrameTimeline.swift.
// This exercises AVFoundation, not UIKit rendering, ONNX or cloud publication.
import Foundation
import AVFoundation

var results: [[String: Any]] = []
for file in CommandLine.arguments.dropFirst() {
  let asset = AVURLAsset(url: URL(fileURLWithPath: file))
  var record: [String: Any] = ["file": file]
  var rows: [[String: Any]] = []
  do {
    let seconds = asset.duration.seconds
    guard seconds.isFinite else { throw VideoFrameTimeline.error("Invalid video duration") }
    let duration = Int((seconds * 1000).rounded())
    guard duration >= 1 && duration <= 120_000 else { throw VideoFrameTimeline.error("Invalid video duration") }
    let count = Int(ceil(Double(duration) / 10000))
    record["duration_ms"] = duration
    record["window_count"] = count
    for index in 0..<count {
      let start = index * duration / count, end = (index + 1) * duration / count
      let times = try VideoFrameTimeline.presentationTimes(asset: asset, bounds: (Double(start), Double(end)))
      var requests = Array(stride(from: start, to: end, by: 1000))
      if requests.last != end - 1 { requests.append(end - 1) }
      let generator = AVAssetImageGenerator(asset: asset)
      generator.appliesPreferredTrackTransform = true
      generator.maximumSize = CGSize(width: 1280, height: 1280)
      generator.requestedTimeToleranceBefore = .zero
      generator.requestedTimeToleranceAfter = .zero
      for request in requests {
        let selected = try VideoFrameTimeline.nearest(Double(request), in: times, startMs: Double(start), endMs: Double(end))
        var actual = CMTime.invalid
        let image = try generator.copyCGImage(at: selected, actualTime: &actual)
        let pts = actual.seconds * 1000
        guard pts.isFinite, pts.rounded() >= Double(start), pts.rounded() < Double(end),
              abs(pts - selected.seconds * 1000) < 0.5 else {
          throw VideoFrameTimeline.error("Unexpected decoded PTS")
        }
        var row: [String: Any] = [:]
        row["window"] = index; row["start_ms"] = start; row["end_ms"] = end
        row["requested_ms"] = request; row["actual_ms"] = pts; row["wire_ms"] = Int(pts.rounded())
        row["width"] = image.width; row["height"] = image.height
        rows.append(row)
      }
    }
    record["status"] = "ACCEPT"
  } catch {
    record["status"] = "REJECT"
    record["error"] = (error as NSError).localizedDescription
  }
  record["decoded_probes"] = rows
  results.append(record)
}
FileHandle.standardOutput.write(try JSONSerialization.data(withJSONObject: results, options: [.prettyPrinted, .sortedKeys]))
