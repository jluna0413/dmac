const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Create a build directory
const buildDir = path.join(__dirname, 'build-basic');
if (!fs.existsSync(buildDir)) {
    fs.mkdirSync(buildDir, { recursive: true });
}

// Create src directory
const srcDir = path.join(buildDir, 'src');
if (!fs.existsSync(srcDir)) {
    fs.mkdirSync(srcDir, { recursive: true });
}

// Create media directory
const mediaDir = path.join(buildDir, 'media');
if (!fs.existsSync(mediaDir)) {
    fs.mkdirSync(mediaDir, { recursive: true });
}

// Copy extension-basic.ts to src/extension.ts
fs.copyFileSync(
    path.join(__dirname, 'src', 'extension-basic.ts'),
    path.join(srcDir, 'extension.ts')
);

// Copy package-basic.json to package.json
fs.copyFileSync(
    path.join(__dirname, 'package-basic.json'),
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
