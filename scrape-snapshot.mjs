#!/usr/bin/env node
// scrape-snapshot.mjs — Fetches the Glide app snapshot and outputs JSON to stdout
import puppeteer from 'puppeteer-core';
import { execSync } from 'child_process';

const CHROME_PATH = process.env.CHROME_PATH || execSync('readlink -f $(which chromium)').toString().trim();

const browser = await puppeteer.launch({
  executablePath: CHROME_PATH,
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
});
const page = await browser.newPage();

let snapshotData = null;
page.on('response', async resp => {
  const url = resp.url();
  if (url.includes('getAppSnapshot')) {
    try {
      const json = await resp.json();
      snapshotData = json;
    } catch(e) {}
  }
});

await page.goto('https://www.airhockeyrank.com', { waitUntil: 'networkidle2', timeout: 30000 });
await new Promise(r => setTimeout(r, 8000));

if (snapshotData && snapshotData.dataSnapshot) {
  // Download the actual data snapshot from the signed URL
  const raw = await page.evaluate(async (url) => {
    const r = await fetch(url);
    return await r.text();
  }, snapshotData.dataSnapshot);
  
  // Decode base64 snapshot and output JSON
  const decoded = JSON.parse(atob(raw));
  process.stdout.write(JSON.stringify(decoded));
} else {
  console.error('No snapshot data captured');
  process.exit(1);
}

await browser.close();
