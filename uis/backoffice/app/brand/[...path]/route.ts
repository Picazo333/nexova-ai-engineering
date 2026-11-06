import { readFile } from "node:fs/promises";
import path from "node:path";

const ROOT = path.join(process.cwd(), "brand");

const TYPES: Record<string, string> = {
  ".svg": "image/svg+xml",
  ".md": "text/markdown; charset=utf-8",
  ".png": "image/png",
};

export async function GET(
  _request: Request,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path: parts } = await context.params;
  if (!parts?.length || parts.some((part) => part === ".." || part.includes("\\") || part.includes("/"))) {
    return new Response(null, { status: 404 });
  }
  const root = path.resolve(ROOT);
  const target = path.resolve(root, ...parts);
  if (target !== root && !target.startsWith(root + path.sep)) {
    return new Response(null, { status: 404 });
  }
  try {
    const body = await readFile(target);
    const type = TYPES[path.extname(target)] ?? "application/octet-stream";
    return new Response(body, {
      headers: {
        "Content-Type": type,
        "Cache-Control": "public, max-age=86400",
      },
    });
  } catch {
    return new Response(null, { status: 404 });
  }
}
