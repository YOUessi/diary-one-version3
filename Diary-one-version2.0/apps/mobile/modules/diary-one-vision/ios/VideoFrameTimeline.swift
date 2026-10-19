import Foundation
import AVFoundation

/// Read presentation timestamps from the actual video samples. Container start
/// and duration need not coincide with the first/last decodable picture.
enum VideoFrameTimeline {
  static func error(_ message: String) -> NSError {
    NSError(domain: "DiaryOneVideoTimeline", code: 1, userInfo: [NSLocalizedDescriptionKey: message])
  }

  static func presentationTimes(asset: AVAsset, bounds: (startMs: Double, endMs: Double)? = nil) throws -> [CMTime] {
    guard let track = asset.tracks(withMediaType: .video).first else {
      throw error("Video has no readable video track")
    }
    let reader = try AVAssetReader(asset: asset)
    let trackEnd = track.timeRange.end
    guard trackEnd.isNumeric, trackEnd.timescale > 0 else { throw error("Video track has invalid timing") }
    var readEnd = asset.duration
    if let bounds = bounds {
      guard bounds.startMs.isFinite, bounds.endMs.isFinite,
            bounds.startMs >= 0, bounds.endMs > bounds.startMs else { throw error("Invalid video probe window") }
      // Include samples within a millisecond of the wire boundary; nearest()
      // still enforces the rounded integer PTS contract. The reader may also
      // return keyframe preroll, which must not become an out-of-window anchor.
      let start = CMTime(seconds: max(0, bounds.startMs - 1) / 1000, preferredTimescale: 1_000_000)
      readEnd = CMTimeMinimum(asset.duration, CMTime(seconds: (bounds.endMs + 1) / 1000, preferredTimescale: 1_000_000))
      guard CMTimeCompare(readEnd, start) > 0 else { throw error("Video window has no readable timeline") }
      reader.timeRange = CMTimeRange(start: start, end: readEnd)
    }
    let output = AVAssetReaderTrackOutput(track: track, outputSettings: nil)
    output.alwaysCopiesSampleData = false
    guard reader.canAdd(output) else { throw error("Video sample reader is unavailable") }
    reader.add(output)
    guard reader.startReading() else { throw reader.error ?? error("Cannot read video samples") }
    defer { reader.cancelReading() }
    var times: [CMTime] = []
    var lastSampleEnd: CMTime?
    while let sample = output.copyNextSampleBuffer() {
      // AVAssetReader also emits zero-sample edit/discontinuity markers. The
      // output PTS applies the track's edit-list offset to real media samples.
      guard CMSampleBufferGetNumSamples(sample) > 0 else { continue }
      let pts = CMSampleBufferGetOutputPresentationTimeStamp(sample)
      if pts.isNumeric && pts.seconds.isFinite && pts.seconds >= 0 {
        times.append(pts)
        let duration = CMSampleBufferGetOutputDuration(sample)
        if duration.isNumeric && CMTimeCompare(duration, .zero) >= 0 {
          let end = CMTimeAdd(pts, duration)
          if lastSampleEnd == nil || CMTimeCompare(end, lastSampleEnd!) > 0 { lastSampleEnd = end }
        }
      }
    }
    if reader.status == .failed { throw reader.error ?? error("Video sample reading failed") }
    guard !times.isEmpty else { throw error("Video contains no presentation timestamps") }
    if CMTimeCompare(readEnd, trackEnd) >= 0 {
      // A truncated MP4 can report reader.completed while omitting final media
      // samples. Require the last sample's actual display duration to cover the
      // video track (not a longer audio track). One track-end timescale tick is
      // the container's declared quantization precision, not a frame-rate guess.
      let timingQuantum = CMTime(value: 1, timescale: trackEnd.timescale)
      guard let lastSampleEnd = lastSampleEnd,
            CMTimeCompare(CMTimeAdd(lastSampleEnd, timingQuantum), trackEnd) >= 0 else {
        throw error("Video media is truncated before the end of its video track")
      }
    }
    return times.sorted { CMTimeCompare($0, $1) < 0 }
  }

  static func nearest(_ requestedMs: Double, in times: [CMTime], startMs: Double, endMs: Double) throws -> CMTime {
    guard requestedMs.isFinite, startMs.isFinite, endMs.isFinite,
          startMs >= 0, endMs > startMs, requestedMs >= startMs, requestedMs < endMs else {
      throw error("Invalid video probe window")
    }
    // The wire contract stores rounded millisecond PTS, so validate that same
    // representation while preserving the exact CMTime for actual decoding.
    let eligible = times.filter {
      let rounded = ($0.seconds * 1000).rounded()
      return rounded >= startMs && rounded < endMs
    }
    guard let chosen = eligible.min(by: {
      let a = abs($0.seconds * 1000 - requestedMs), b = abs($1.seconds * 1000 - requestedMs)
      return a == b ? CMTimeCompare($0, $1) < 0 : a < b
    }) else { throw error("Video window has no real frame: [\(startMs), \(endMs)) ms") }
    return chosen
  }
}
