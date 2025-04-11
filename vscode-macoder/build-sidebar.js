const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Create a build directory
const buildDir = path.join(__dirname, 'build-sidebar');
if (!fs.existsSync(buildDir)) {
    fs.mkdirSync(buildDir, { recursive: true });
}

// Create src directory structure
const srcDir = path.join(buildDir, 'src');
if (!fs.existsSync(srcDir)) {
    fs.mkdirSync(srcDir, { recursive: true });
}

const uiDir = path.join(srcDir, 'ui');
if (!fs.existsSync(uiDir)) {
    fs.mkdirSync(uiDir, { recursive: true });
}

const sidebarDir = path.join(uiDir, 'sidebar');
if (!fs.existsSync(sidebarDir)) {
    fs.mkdirSync(sidebarDir, { recursive: true });
}

// Create media directory structure
const mediaDir = path.join(buildDir, 'media');
if (!fs.existsSync(mediaDir)) {
    fs.mkdirSync(mediaDir, { recursive: true });
}

const mediaSidebarDir = path.join(mediaDir, 'sidebar');
if (!fs.existsSync(mediaSidebarDir)) {
    fs.mkdirSync(mediaSidebarDir, { recursive: true });
}

const mediaIconsDir = path.join(mediaDir, 'icons');
if (!fs.existsSync(mediaIconsDir)) {
    fs.mkdirSync(mediaIconsDir, { recursive: true });
}

// Copy extension-sidebar.ts to src/extension.ts
fs.copyFileSync(
    path.join(__dirname, 'src', 'extension-sidebar.ts'),
    path.join(srcDir, 'extension.ts')
);

// Copy UI files
fs.copyFileSync(
    path.join(__dirname, 'src', 'ui', 'sidebar', 'index.ts'),
    path.join(sidebarDir, 'index.ts')
);

fs.copyFileSync(
    path.join(__dirname, 'src', 'ui', 'sidebar', 'chat-view-provider.ts'),
    path.join(sidebarDir, 'chat-view-provider.ts')
);

fs.copyFileSync(
    path.join(__dirname, 'src', 'ui', 'sidebar', 'code-generation-view-provider.ts'),
    path.join(sidebarDir, 'code-generation-view-provider.ts')
);

fs.copyFileSync(
    path.join(__dirname, 'src', 'ui', 'sidebar', 'brainstorming-view-provider.ts'),
    path.join(sidebarDir, 'brainstorming-view-provider.ts')
);

fs.copyFileSync(
    path.join(__dirname, 'src', 'ui', 'sidebar', 'sandbox-view-provider.ts'),
    path.join(sidebarDir, 'sandbox-view-provider.ts')
);

fs.copyFileSync(
    path.join(__dirname, 'src', 'ui', 'sidebar', 'settings-view-provider.ts'),
    path.join(sidebarDir, 'settings-view-provider.ts')
);

// Copy media files
fs.copyFileSync(
    path.join(__dirname, 'media', 'icons', 'macoder-icon.svg'),
    path.join(mediaIconsDir, 'macoder-icon.svg')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'icons', 'chat-icon.svg'),
    path.join(mediaIconsDir, 'chat-icon.svg')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'icons', 'code-icon.svg'),
    path.join(mediaIconsDir, 'code-icon.svg')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'icons', 'brainstorm-icon.svg'),
    path.join(mediaIconsDir, 'brainstorm-icon.svg')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'icons', 'sandbox-icon.svg'),
    path.join(mediaIconsDir, 'sandbox-icon.svg')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'icons', 'settings-icon.svg'),
    path.join(mediaIconsDir, 'settings-icon.svg')
);

// Copy sidebar JS and CSS files
fs.copyFileSync(
    path.join(__dirname, 'media', 'sidebar', 'chat.js'),
    path.join(mediaSidebarDir, 'chat.js')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'sidebar', 'chat.css'),
    path.join(mediaSidebarDir, 'chat.css')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'sidebar', 'code-generation.js'),
    path.join(mediaSidebarDir, 'code-generation.js')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'sidebar', 'code-generation.css'),
    path.join(mediaSidebarDir, 'code-generation.css')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'sidebar', 'brainstorming.js'),
    path.join(mediaSidebarDir, 'brainstorming.js')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'sidebar', 'brainstorming.css'),
    path.join(mediaSidebarDir, 'brainstorming.css')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'sidebar', 'sandbox.js'),
    path.join(mediaSidebarDir, 'sandbox.js')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'sidebar', 'sandbox.css'),
    path.join(mediaSidebarDir, 'sandbox.css')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'sidebar', 'settings.js'),
    path.join(mediaSidebarDir, 'settings.js')
);

fs.copyFileSync(
    path.join(__dirname, 'media', 'sidebar', 'settings.css'),
    path.join(mediaSidebarDir, 'settings.css')
);

// Copy package.json
fs.copyFileSync(
    path.join(__dirname, 'package-sidebar.json'),
    path.join(buildDir, 'package.json')
);

// Copy README.md
fs.copyFileSync(
    path.join(__dirname, 'README.md'),
    path.join(buildDir, 'README.md')
);

// Copy CHANGELOG.md
fs.copyFileSync(
    path.join(__dirname, 'CHANGELOG.md'),
    path.join(buildDir, 'CHANGELOG.md')
);

// Create a minimal LICENSE file
const licenseContent = `MIT License

Copyright (c) 2025 DMac

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.`;

fs.writeFileSync(path.join(buildDir, 'LICENSE'), licenseContent);

// Create a minimal tsconfig.json
const tsconfigContent = {
    "compilerOptions": {
        "module": "commonjs",
        "target": "ES2020",
        "outDir": "out",
        "lib": ["ES2020"],
        "sourceMap": true,
        "rootDir": "src",
        "strict": true,
        "noImplicitReturns": true,
        "noFallthroughCasesInSwitch": true,
        "noUnusedLocals": false,
        "noUnusedParameters": false,
        "esModuleInterop": true
    },
    "exclude": ["node_modules", ".vscode-test"]
};

fs.writeFileSync(
    path.join(buildDir, 'tsconfig.json'),
    JSON.stringify(tsconfigContent, null, 2)
);

// Create a minimal .vscodeignore file
const vscodeignoreContent = `
.vscode/**
.vscode-test/**
node_modules/**
.gitignore
.yarnrc
webpack.config.js
vsc-extension-quickstart.md
**/.eslintrc.json
**/*.map
`;

fs.writeFileSync(path.join(buildDir, '.vscodeignore'), vscodeignoreContent);

// Change to the build directory and install dependencies
console.log('Installing dependencies...');
execSync('npm install', { cwd: buildDir, stdio: 'inherit' });

// Compile TypeScript
console.log('Compiling TypeScript...');
execSync('npx tsc -p .', { cwd: buildDir, stdio: 'inherit' });

// Package the extension
console.log('Packaging extension...');
execSync('npx vsce package', { cwd: buildDir, stdio: 'inherit' });

// Copy the VSIX file to the parent directory
const vsixFile = fs.readdirSync(buildDir).find(file => file.endsWith('.vsix'));
if (vsixFile) {
    fs.copyFileSync(path.join(buildDir, vsixFile), path.join(__dirname, vsixFile));
    console.log(`Successfully packaged extension: ${vsixFile}`);
}
