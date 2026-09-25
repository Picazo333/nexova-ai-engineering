import { spawn } from 'node:child_process'
import { writeFile } from 'node:fs/promises'

const [chrome, url, output, widthRaw = '1440', heightRaw = '900'] = process.argv.slice(2)
if (!chrome || !url || !output) {
  throw new Error('usage: node capture-browser-evidence.mjs <chrome> <url> <output> [width] [height]')
}

const width = Number(widthRaw)
const height = Number(heightRaw)
const port = 9222
const profile = `/tmp/nexova-cdp-${process.pid}`

const proc = spawn(
  chrome,
  [
    '--headless=new',
    '--no-sandbox',
    '--disable-gpu',
    '--hide-scrollbars',
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profile}`,
    `--window-size=${width},${height}`,
    url,
  ],
  { stdio: 'ignore' },
)

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

try {
  let pages
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json`)
      pages = await response.json()
      if (pages?.length) break
    } catch {}
    await sleep(100)
  }
  if (!pages?.length) throw new Error('Chrome DevTools endpoint did not become ready')

  const page = pages.find((entry) => entry.type === 'page') ?? pages[0]
  const ws = new WebSocket(page.webSocketDebuggerUrl)
  await new Promise((resolve, reject) => {
    ws.addEventListener('open', resolve, { once: true })
    ws.addEventListener('error', reject, { once: true })
  })

  let nextId = 1
  const pending = new Map()
  ws.addEventListener('message', (event) => {
    const message = JSON.parse(event.data)
    if (!message.id || !pending.has(message.id)) return
    const { resolve, reject } = pending.get(message.id)
    pending.delete(message.id)
    if (message.error) reject(new Error(message.error.message))
    else resolve(message.result)
  })

  const send = (method, params = {}) =>
    new Promise((resolve, reject) => {
      const id = nextId++
      pending.set(id, { resolve, reject })
      ws.send(JSON.stringify({ id, method, params }))
    })

  await send('Page.enable')
  await send('Runtime.enable')
  await send('Runtime.evaluate', {
    expression: 'document.fonts && document.fonts.ready',
    awaitPromise: true,
  })
  await sleep(700)

  const geometry = await send('Runtime.evaluate', {
    expression:
      '({height: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight), step: Math.max(600, Math.floor(window.innerHeight * 0.72))})',
    returnByValue: true,
  })
  const { height: documentHeight, step } = geometry.result.value

  for (let y = 0; y < documentHeight; y += step) {
    await send('Runtime.evaluate', { expression: `window.scrollTo(0, ${y})` })
    await sleep(180)
  }
  await send('Runtime.evaluate', { expression: 'window.scrollTo(0, 0)' })
  await sleep(850)

  const metrics = await send('Page.getLayoutMetrics')
  const contentSize = metrics.cssContentSize ?? metrics.contentSize
  const screenshot = await send('Page.captureScreenshot', {
    format: 'png',
    fromSurface: true,
    captureBeyondViewport: true,
    clip: {
      x: 0,
      y: 0,
      width: Math.ceil(contentSize.width),
      height: Math.ceil(contentSize.height),
      scale: 1,
    },
  })
  await writeFile(output, Buffer.from(screenshot.data, 'base64'))
  ws.close()
} finally {
  proc.kill('SIGTERM')
}
