import puppeteer from 'puppeteer';
import { mkdir } from 'fs/promises';

const SCREENSHOTS_DIR = './test-screenshots';
const URL = 'http://localhost:3000';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function takeScreenshot(page, name, viewport) {
  await mkdir(SCREENSHOTS_DIR, { recursive: true });
  const filename = `${SCREENSHOTS_DIR}/${name}_${viewport.width}x${viewport.height}.png`;
  await page.screenshot({ path: filename, fullPage: false });
  console.log(`  ✓ Screenshot saved: ${filename}`);
}

async function testLayout(name, viewport) {
  console.log(`\n📱 Testing ${name} (${viewport.width}x${viewport.height})`);

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport(viewport);

  // Navigate to page
  console.log(`  → Navigating to ${URL}`);
  await page.goto(URL, { waitUntil: 'networkidle0', timeout: 10000 });

  // Wait for page to load
  await sleep(2000);

  // Take initial screenshot
  await takeScreenshot(page, '01_initial', viewport);

  // Check if session is initialized
  const sessionId = await page.evaluate(() => {
    const storage = localStorage.getItem('termai_session_id');
    return storage;
  });
  console.log(`  → Session ID: ${sessionId || 'Not found (initializing...)'}`);

  // Wait a bit more for any animations
  await sleep(1000);

  // Take final screenshot
  await takeScreenshot(page, '02_final', viewport);

  // Check layout elements
  const layoutInfo = await page.evaluate(() => {
    const input = document.querySelector('textarea[placeholder*="Type a command"]');
    // Find statusbar by looking for session info or status indicator
    const statusBar = Array.from(document.querySelectorAll('div')).find(el =>
      el.textContent.includes('Session:') || el.textContent.includes('Ready') || el.textContent.includes('Processing')
    );
    const fixedContainer = document.querySelector('.fixed.bottom-0.z-50');

    const inputRect = input?.getBoundingClientRect();
    const statusBarRect = statusBar?.getBoundingClientRect();
    const containerRect = fixedContainer?.getBoundingClientRect();

    return {
      inputVisible: !!input && inputRect.top < window.innerHeight && inputRect.bottom > 0,
      statusBarVisible: !!statusBar && statusBarRect.top < window.innerHeight && statusBarRect.bottom > 0,
      inputPosition: inputRect ? { top: inputRect.top, bottom: inputRect.bottom } : null,
      statusBarPosition: statusBarRect ? { top: statusBarRect.top, bottom: statusBarRect.bottom } : null,
      containerPosition: containerRect ? { top: containerRect.top, bottom: containerRect.bottom } : null,
      windowHeight: window.innerHeight,
      windowWidth: window.innerWidth,
    };
  });

  console.log(`  → Input visible: ${layoutInfo.inputVisible}`);
  console.log(`  → StatusBar visible: ${layoutInfo.statusBarVisible}`);
  console.log(`  → Window size: ${layoutInfo.windowWidth}x${layoutInfo.windowHeight}`);

  if (layoutInfo.inputPosition && layoutInfo.statusBarPosition) {
    const statusBarAboveInput = layoutInfo.statusBarPosition.bottom <= layoutInfo.inputPosition.top;
    const statusBarBelowInput = layoutInfo.statusBarPosition.top >= layoutInfo.inputPosition.bottom;
    const elementsOverlap = layoutInfo.statusBarPosition.top < layoutInfo.inputPosition.bottom &&
                               layoutInfo.statusBarPosition.bottom > layoutInfo.inputPosition.top;

    console.log(`  → StatusBar position: top=${Math.round(layoutInfo.statusBarPosition.top)}px, bottom=${Math.round(layoutInfo.statusBarPosition.bottom)}px`);
    console.log(`  → Input position: top=${Math.round(layoutInfo.inputPosition.top)}px, bottom=${Math.round(layoutInfo.inputPosition.bottom)}px`);

    if (statusBarAboveInput) {
      console.log(`  ✗ ERROR: StatusBar is ABOVE input!`);
    } else if (elementsOverlap) {
      console.log(`  ✗ ERROR: StatusBar and Input OVERLAP!`);
    } else {
      console.log(`  ✓ Correct: StatusBar is below input`);
    }
  }

  await browser.close();
  return layoutInfo;
}

async function runTests() {
  console.log('🚀 Starting layout tests...\n');

  // Desktop test
  const desktopResults = await testLayout('Desktop', {
    width: 1920,
    height: 1080,
    deviceScaleFactor: 1,
  });

  // Laptop test
  const laptopResults = await testLayout('Laptop', {
    width: 1366,
    height: 768,
    deviceScaleFactor: 1,
  });

  // Mobile Portrait
  const mobilePortraitResults = await testLayout('Mobile Portrait', {
    width: 390,
    height: 844,
    deviceScaleFactor: 3,
    isMobile: true,
  });

  // Mobile Landscape
  const mobileLandscapeResults = await testLayout('Mobile Landscape', {
    width: 844,
    height: 390,
    deviceScaleFactor: 3,
    isMobile: true,
  });

  // iPhone 12 Pro
  const iPhoneResults = await testLayout('iPhone 12 Pro', {
    width: 390,
    height: 844,
    deviceScaleFactor: 3,
    isMobile: true,
  });

  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST RESULTS SUMMARY');
  console.log('='.repeat(60));

  const allTests = [
    { name: 'Desktop', results: desktopResults },
    { name: 'Laptop', results: laptopResults },
    { name: 'Mobile Portrait', results: mobilePortraitResults },
    { name: 'Mobile Landscape', results: mobileLandscapeResults },
    { name: 'iPhone', results: iPhoneResults },
  ];

  let passCount = 0;
  let failCount = 0;

  allTests.forEach(test => {
    const pass = test.results.inputVisible && test.results.statusBarVisible;
    if (pass) {
      passCount++;
      console.log(`✅ ${test.name}: PASS (both input and statusbar visible)`);
    } else {
      failCount++;
      console.log(`❌ ${test.name}: FAIL`);
      console.log(`   Input visible: ${test.results.inputVisible}`);
      console.log(`   StatusBar visible: ${test.results.statusBarVisible}`);
    }
  });

  console.log('\n' + '='.repeat(60));
  console.log(`Total: ${passCount} passed, ${failCount} failed`);
  console.log(`Screenshots saved to: ${SCREENSHOTS_DIR}/`);
  console.log('='.repeat(60));

  if (failCount > 0) {
    process.exit(1);
  }
}

runTests().catch(err => {
  console.error('❌ Test failed:', err);
  process.exit(1);
});
