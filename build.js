const esbuild = require('esbuild');
const fs = require('fs');
const path = require('path');

const watchMode = process.argv.includes('--watch');
const isFirefox = process.argv.includes('--firefox');
const outputDir = isFirefox ? 'dist-firefox' : 'dist';

// Ensure output directory exists
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Build configuration
const buildOptions = {
  entryPoints: [
    'extension/background/login-detector.ts',
    'extension/popup/popup.ts'
  ],
  bundle: true,
  outdir: outputDir,
  platform: 'browser',
  target: isFirefox ? 'firefox109' : 'chrome100',
  format: 'iife',
  sourcemap: true,
  logLevel: 'info',
  define: {
    'process.env.NODE_ENV': '"production"'
  }
};

async function build() {
  try {
    if (watchMode) {
      const context = await esbuild.context(buildOptions);
      await context.watch();
      console.log('Watching for changes...');
    } else {
      await esbuild.build(buildOptions);

      // Copy manifest and static files
      const manifestSource = isFirefox ? 'extension/manifest-firefox.json' : 'extension/manifest.json';
      if (fs.existsSync(manifestSource)) {
        fs.copyFileSync(manifestSource, `${outputDir}/manifest.json`);
      }
      if (fs.existsSync('extension/popup/popup.html')) {
        fs.copyFileSync('extension/popup/popup.html', `${outputDir}/popup.html`);
      }
      if (fs.existsSync('extension/popup/popup.css')) {
        fs.copyFileSync('extension/popup/popup.css', `${outputDir}/popup.css`);
      }
      if (fs.existsSync('extension/icons')) {
        fs.cpSync('extension/icons', `${outputDir}/icons`, { recursive: true });
      }

      console.log(`Build complete! Output: ${outputDir}/`);
    }
  } catch (error) {
    console.error('Build failed:', error);
    process.exit(1);
  }
}

build();
