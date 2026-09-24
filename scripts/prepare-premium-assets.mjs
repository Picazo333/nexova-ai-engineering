import fs from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const websiteRoot = process.cwd();
const repoRoot = path.resolve(websiteRoot, "../..");
const sourceRoot = path.join(repoRoot, "packages/design-system/assets");
const outputRoot = path.join(websiteRoot, "public/runtime");

await fs.mkdir(outputRoot, { recursive: true });

const jobs = [
  {
    source: "a1-hero-desktop.png",
    family: "a1-hero-desktop",
    widths: [640, 960],
    avifQuality: 60,
    webpQuality: 84,
  },
  {
    source: "a1-hero-mobile.png",
    family: "a1-hero-mobile",
    widths: [480, 768],
    avifQuality: 60,
    webpQuality: 84,
  },
  {
    source: "a2-crimson-fibrous.png",
    family: "a2-crimson-fibrous",
    widths: [640, 960],
    avifQuality: 58,
    webpQuality: 82,
  },
];

const manifest = {};

for (const job of jobs) {
  const sourcePath = path.join(sourceRoot, job.source);
  const metadata = await sharp(sourcePath).metadata();
  if (!metadata.width || !metadata.height) {
    throw new Error(`Could not read dimensions for ${job.source}`);
  }

  manifest[job.family] = {
    source: job.source,
    sourceWidth: metadata.width,
    sourceHeight: metadata.height,
    outputs: [],
  };

  for (const requestedWidth of job.widths) {
    const width = Math.min(requestedWidth, metadata.width);
    const ratio = width / metadata.width;
    const height = Math.max(1, Math.round(metadata.height * ratio));

    for (const format of ["avif", "webp"]) {
      const fileName = `${job.family}-${width}.${format}`;
      const outputPath = path.join(outputRoot, fileName);
      let pipeline = sharp(sourcePath).resize({
        width,
        height,
        fit: "fill",
        withoutEnlargement: true,
      });

      pipeline = format === "avif"
        ? pipeline.avif({ quality: job.avifQuality, effort: 4 })
        : pipeline.webp({ quality: job.webpQuality, effort: 4 });

      await pipeline.toFile(outputPath);
      const stat = await fs.stat(outputPath);
      manifest[job.family].outputs.push({
        file: `/runtime/${fileName}`,
        format,
        width,
        height,
        bytes: stat.size,
      });
    }
  }
}

await fs.writeFile(
  path.join(outputRoot, "manifest.json"),
  JSON.stringify(manifest, null, 2) + "\n",
);

console.log(JSON.stringify(manifest, null, 2));
