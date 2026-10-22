/** RGB preprocessing matching the frozen Pillow bicubic/center-crop contract.
 * Work on decoded pixels, never compressed PNG/JPEG bytes. */
export type Pixels = { width: number; height: number; data: Uint8Array };

export function roundEven(x: number): number {
  const lo = Math.floor(x);
  return x - lo === 0.5 ? lo + (lo % 2) : Math.round(x);
}

function cubic(x: number): number {
  x = Math.abs(x);
  if (x < 1) return ((1.5 * x - 2.5) * x) * x + 1;
  if (x < 2) return ((-0.5 * x + 2.5) * x - 4) * x + 2;
  return 0;
}

function coefficients(input: number, output: number) {
  const scale = input / output, filterScale = Math.max(1, scale);
  return Array.from({ length: output }, (_, i) => {
    const center = (i + 0.5) * scale;
    const start = Math.max(0, Math.trunc(center - 2 * filterScale + 0.5));
    const end = Math.min(input, Math.trunc(center + 2 * filterScale + 0.5));
    const weights = Array.from({ length: end - start }, (_, j) => cubic((j + start - center + 0.5) / filterScale));
    const sum = weights.reduce((a, b) => a + b, 0);
    // Pillow's 8-bit separable resampler uses signed 22-bit fixed coefficients.
    return { start, weights: weights.map(w => Math.trunc(w / sum * 4194304 + (w < 0 ? -0.5 : 0.5))) };
  });
}

function* resizeSteps(image: Pixels, width: number, height: number): Generator<void, Pixels> {
  const channels = 4;
  if (image.data.length !== image.width * image.height * channels) throw new Error('RGBA pixel size mismatch');
  const horizontal = new Uint8Array(width * image.height * channels);
  const xc = coefficients(image.width, width), yc = coefficients(image.height, height);
  for (let y = 0; y < image.height; y++) {
    for (let x = 0; x < width; x++) {
      for (let c = 0; c < channels; c++) {
        let sum = 2097152;
        for (let j = 0; j < xc[x].weights.length; j++) sum += image.data[(y * image.width + xc[x].start + j) * 4 + c] * xc[x].weights[j];
        horizontal[(y * width + x) * 4 + c] = Math.max(0, Math.min(255, Math.floor(sum / 4194304)));
      }
    }
    if (y % 4 === 3) yield;
  }
  const output = new Uint8Array(width * height * channels);
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      for (let c = 0; c < channels; c++) {
        let sum = 2097152;
        for (let j = 0; j < yc[y].weights.length; j++) sum += horizontal[((yc[y].start + j) * width + x) * 4 + c] * yc[y].weights[j];
        output[(y * width + x) * 4 + c] = Math.max(0, Math.min(255, Math.floor(sum / 4194304)));
      }
    }
    if (y % 4 === 3) yield;
  }
  return { width, height, data: output };
}

export function resizeBicubic(image: Pixels, width: number, height: number): Pixels {
  const steps = resizeSteps(image, width, height);
  let next = steps.next();
  while (!next.done) next = steps.next();
  return next.value;
}

function* preprocessSteps(image: Pixels): Generator<void, Float32Array> {
  const short = 269, crop = 256;
  const width = image.width <= image.height ? short : Math.floor(short * image.width / image.height);
  const height = image.width <= image.height ? Math.floor(short * image.height / image.width) : short;
  const resized = yield* resizeSteps(image, width, height);
  const left = roundEven((width - crop) / 2), top = roundEven((height - crop) / 2);
  const output = new Float32Array(3 * crop * crop);
  for (let y = 0; y < crop; y++) for (let x = 0; x < crop; x++) for (let c = 0; c < 3; c++) {
    output[c * crop * crop + y * crop + x] = resized.data[((y + top) * width + x + left) * 4 + c] / 255;
  }
  return output;
}

export function preprocess(image: Pixels): Float32Array {
  const steps = preprocessSteps(image);
  let next = steps.next();
  while (!next.done) next = steps.next();
  return next.value;
}

// The same fixed-point kernel and operation order as the reference path.
// Yield within each image: yielding only between images still blocks Hermes
// for seconds on large frames, preventing navigation and cancellation.
export async function preprocessAsync(image: Pixels, assertCurrent: () => void = () => {}): Promise<Float32Array> {
  const steps = preprocessSteps(image);
  let lastYield = 0;
  try {
    for (;;) {
      assertCurrent();
      const next = steps.next();
      if (next.done) return next.value;
      // A native timer for every four rows makes even a fast Release kernel
      // wait for hundreds of event-loop turns per frame. Check in small row
      // chunks, but yield on a time budget (and once at the start).
      if (Date.now() - lastYield >= 12) {
        await new Promise<void>(resolve => setTimeout(resolve, 0));
        lastYield = Date.now();
      }
    }
  } finally {
    steps.return(new Float32Array(0));
  }
}

export function pixelQuality(image: Pixels) {
  let sum = 0, dark = 0, lap = 0, lap2 = 0, interior = 0;
  const n = image.width * image.height, gray = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    gray[i] = 0.299 * image.data[i * 4] + 0.587 * image.data[i * 4 + 1] + 0.114 * image.data[i * 4 + 2];
    sum += gray[i]; if (gray[i] <= 32) dark++;
  }
  for (let y = 1; y < image.height - 1; y++) for (let x = 1; x < image.width - 1; x++) {
    const i = y * image.width + x;
    const v = gray[i - 1] + gray[i + 1] + gray[i - image.width] + gray[i + image.width] - 4 * gray[i];
    lap += v; lap2 += v * v; interior++;
  }
  const meanLuma = sum / n, darkPixelRatio = dark / n;
  const sharpness = interior ? Math.max(0, lap2 / interior - (lap / interior) ** 2) : 0;
  const blank = meanLuma <= 24 && darkPixelRatio >= 0.95 && sharpness <= 100;
  return { meanLuma, darkPixelRatio, sharpness, eligibleForSelection: !blank,
    qualityReasonCodes: blank ? ['BLANK_OR_BLACK_FRAME'] : [] };
}
