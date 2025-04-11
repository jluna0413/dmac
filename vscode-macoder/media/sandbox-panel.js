// @ts-check

(function() {
    // Get VS Code API
    const vscode = acquireVsCodeApi();
    
    // Elements
    let testsTab;
    let executeTab;
    let testsView;
    let testView;
    let executeView;
    let testsList;
    let newTestButton;
    let backToTestsButton;
    let runTestButton;
    let deleteTestButton;
    let testName;
    let testLanguage;
    let testCode;
    let testResultSection;
    let testResultStatus;
    let testResultTime;
    let testResultOutput;
    let testResultError;
    let testResultErrorSection;
    let executeLanguage;
    let executeCode;
    let executeButton;
    let saveAsTestButton;
    let executeResultSection;
    let executeResultStatus;
    let executeResultTime;
    let executeResultOutput;
    let executeResultError;
    let executeResultErrorSection;
    
    // State
    let tests = [];
    let activeTestId = null;
    let executeResult = null;
    
    // Initialize
    document.addEventListener('DOMContentLoaded', () => {
        // Get elements
        testsTab = document.getElementById('testsTab');
        executeTab = document.getElementById('executeTab');
        testsView = document.getElementById('testsView');
        testView = document.getElementById('testView');
        executeView = document.getElementById('executeView');
        testsList = document.getElementById('testsList');
        newTestButton = document.getElementById('newTestButton');
        backToTestsButton = document.getElementById('backToTestsButton');
        runTestButton = document.getElementById('runTestButton');
        deleteTestButton = document.getElementById('deleteTestButton');
        testName = document.getElementById('testName');
        testLanguage = document.getElementById('testLanguage');
        testCode = document.getElementById('testCode');
        testResultSection = document.getElementById('testResultSection');
        testResultStatus = document.getElementById('testResultStatus');
        testResultTime = document.getElementById('testResultTime');
        testResultOutput = document.getElementById('testResultOutput');
        testResultError = document.getElementById('testResultError');
        testResultErrorSection = document.getElementById('testResultErrorSection');
        executeLanguage = document.getElementById('executeLanguage');
        executeCode = document.getElementById('executeCode');
        executeButton = document.getElementById('executeButton');
        saveAsTestButton = document.getElementById('saveAsTestButton');
        executeResultSection = document.getElementById('executeResultSection');
        executeResultStatus = document.getElementById('executeResultStatus');
        executeResultTime = document.getElementById('executeResultTime');
        executeResultOutput = document.getElementById('executeResultOutput');
        executeResultError = document.getElementById('executeResultError');
        executeResultErrorSection = document.getElementById('executeResultErrorSection');
        
        // Set up event listeners
        setupEventListeners();
        
        // Restore state
        const state = vscode.getState();
        if (state) {
            tests = state.tests || [];
            activeTestId = state.activeTestId || null;
            executeResult = state.executeResult || null;
        }
    });
    
    // Set up event listeners
    function setupEventListeners() {
        // Tab navigation
        testsTab.addEventListener('click', () => {
            showTests();
        });
        
        executeTab.addEventListener('click', () => {
            showExecute();
        });
        
        // Test actions
        newTestButton.addEventListener('click', () => {
            createNewTest();
        });
        
        backToTestsButton.addEventListener('click', () => {
            showTests();
        });
        
        runTestButton.addEventListener('click', () => {
            runTest();
        });
        
        deleteTestButton.addEventListener('click', () => {
            deleteTest();
        });
        
        // Execute actions
        executeButton.addEventListener('click', () => {
            executeCode();
        });
        
        saveAsTestButton.addEventListener('click', () => {
            saveAsTest();
        });
    }
    
    // Handle messages from the extension
    window.addEventListener('message', event => {
        const message = event.data;
        
        switch (message.command) {
            case 'updateTestsList':
                tests = message.tests;
                renderTestsList();
                saveState();
                break;
            case 'updateTestView':
                renderTestView(message.test);
                saveState();
                break;
            case 'updateExecuteView':
                renderExecuteView();
                saveState();
                break;
            case 'updateExecuteResult':
                executeResult = message.result;
                renderExecuteResult();
                saveState();
                break;
        }
    });
    
    // Save state
    function saveState() {
        vscode.setState({
            tests,
            activeTestId,
            executeResult
        });
    }
    
    // Show tests view
    function showTests() {
        testsTab.classList.add('active');
        executeTab.classList.remove('active');
        
        testsView.classList.remove('hidden');
        testView.classList.add('hidden');
        executeView.classList.add('hidden');
        
        vscode.postMessage({
            command: 'showTests'
        });
    }
    
    // Show execute view
    function showExecute() {
        testsTab.classList.remove('active');
        executeTab.classList.add('active');
        
        testsView.classList.add('hidden');
        testView.classList.add('hidden');
        executeView.classList.remove('hidden');
        
        vscode.postMessage({
            command: 'showExecute'
        });
    }
    
    // Create a new test
    function createNewTest() {
        // Show input dialog
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.placeholder = 'Test Name';
        
        const codeInput = document.createElement('textarea');
        codeInput.placeholder = 'Test Code';
        
        const languageSelect = document.createElement('select');
        languageSelect.innerHTML = `
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="python">Python</option>
            <option value="java">Java</option>
            <option value="c">C</option>
            <option value="cpp">C++</option>
            <option value="csharp">C#</option>
            <option value="go">Go</option>
            <option value="ruby">Ruby</option>
            <option value="php">PHP</option>
            <option value="rust">Rust</option>
            <option value="shell">Shell</option>
            <option value="powershell">PowerShell</option>
        `;
        
        const dialog = document.createElement('div');
        dialog.className = 'dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <h2>Create New Test</h2>
                <div class="dialog-form">
                    <div class="form-group">
                        <label for="name">Name:</label>
                        <div id="nameContainer"></div>
                    </div>
                    <div class="form-group">
                        <label for="language">Language:</label>
                        <div id="languageContainer"></div>
                    </div>
                    <div class="form-group">
                        <label for="code">Code:</label>
                        <div id="codeContainer"></div>
                    </div>
                </div>
                <div class="dialog-buttons">
                    <button id="cancelButton" class="secondary-button">Cancel</button>
                    <button id="createButton" class="primary-button">Create</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        document.getElementById('nameContainer').appendChild(nameInput);
        document.getElementById('languageContainer').appendChild(languageSelect);
        document.getElementById('codeContainer').appendChild(codeInput);
        
        const cancelButton = document.getElementById('cancelButton');
        const createButton = document.getElementById('createButton');
        
        cancelButton.addEventListener('click', () => {
            document.body.removeChild(dialog);
        });
        
        createButton.addEventListener('click', () => {
            const name = nameInput.value.trim();
            const language = languageSelect.value;
            const code = codeInput.value.trim();
            
            if (!name) {
                alert('Please enter a name');
                return;
            }
            
            if (!code) {
                alert('Please enter code');
                return;
            }
            
            vscode.postMessage({
                command: 'createTest',
                name,
                code,
                language
            });
            
            document.body.removeChild(dialog);
        });
    }
    
    // Render tests list
    function renderTestsList() {
        if (tests.length === 0) {
            testsList.innerHTML = '<div class="empty-state">No tests yet</div>';
            return;
        }
        
        testsList.innerHTML = '';
        
        for (const test of tests) {
            const testElement = document.createElement('div');
            testElement.className = 'test-item';
            testElement.innerHTML = `
                <div class="test-item-header">
                    <h3>${test.name}</h3>
                    <div class="test-item-actions">
                        <button class="delete-button">Delete</button>
                    </div>
                </div>
                <div class="test-item-language">${test.language}</div>
                <div class="test-item-meta">
                    <span>${formatDate(test.createdAt)}</span>
                    <span class="test-status ${test.result ? (test.result.success ? 'success' : 'error') : ''}">
                        ${test.result ? (test.result.success ? 'Passed' : 'Failed') : 'Not Run'}
                    </span>
                </div>
            `;
            
            testElement.addEventListener('click', event => {
                if (!event.target.classList.contains('delete-button')) {
                    openTest(test.id);
                }
            });
            
            const deleteButton = testElement.querySelector('.delete-button');
            deleteButton.addEventListener('click', event => {
                event.stopPropagation();
                deleteTestById(test.id);
            });
            
            testsList.appendChild(testElement);
        }
    }
    
    // Open a test
    function openTest(testId) {
        activeTestId = testId;
        
        vscode.postMessage({
            command: 'openTest',
            testId
        });
    }
    
    // Delete a test by ID
    function deleteTestById(testId) {
        if (confirm('Are you sure you want to delete this test?')) {
            vscode.postMessage({
                command: 'deleteTest',
                testId
            });
        }
    }
    
    // Delete the active test
    function deleteTest() {
        if (!activeTestId) {
            return;
        }
        
        deleteTestById(activeTestId);
    }
    
    // Run the active test
    function runTest() {
        if (!activeTestId) {
            return;
        }
        
        vscode.postMessage({
            command: 'runTest',
            testId: activeTestId
        });
    }
    
    // Render test view
    function renderTestView(test) {
        activeTestId = test.id;
        
        testsTab.classList.add('active');
        executeTab.classList.remove('active');
        
        testsView.classList.add('hidden');
        testView.classList.remove('hidden');
        executeView.classList.add('hidden');
        
        testName.textContent = test.name;
        testLanguage.textContent = test.language;
        testCode.textContent = test.code;
        
        // Render result if available
        if (test.result) {
            testResultSection.classList.remove('hidden');
            testResultStatus.textContent = test.result.success ? 'Success' : 'Failed';
            testResultStatus.className = test.result.success ? 'success' : 'error';
            testResultTime.textContent = test.result.executionTime ? test.result.executionTime.toString() : '0';
            testResultOutput.textContent = test.result.output || '';
            
            if (test.result.error) {
                testResultErrorSection.classList.remove('hidden');
                testResultError.textContent = test.result.error;
            } else {
                testResultErrorSection.classList.add('hidden');
            }
        } else {
            testResultSection.classList.add('hidden');
        }
    }
    
    // Render execute view
    function renderExecuteView() {
        testsTab.classList.remove('active');
        executeTab.classList.add('active');
        
        testsView.classList.add('hidden');
        testView.classList.add('hidden');
        executeView.classList.remove('hidden');
        
        // Render result if available
        if (executeResult) {
            renderExecuteResult();
        } else {
            executeResultSection.classList.add('hidden');
        }
    }
    
    // Execute code
    function executeCode() {
        const code = executeCode.value.trim();
        const language = executeLanguage.value;
        
        if (!code) {
            alert('Please enter code');
            return;
        }
        
        vscode.postMessage({
            command: 'executeCode',
            code,
            language
        });
    }
    
    // Save as test
    function saveAsTest() {
        const code = executeCode.value.trim();
        const language = executeLanguage.value;
        
        if (!code) {
            alert('Please enter code');
            return;
        }
        
        // Show input dialog for test name
        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.placeholder = 'Test Name';
        
        const dialog = document.createElement('div');
        dialog.className = 'dialog';
        dialog.innerHTML = `
            <div class="dialog-content">
                <h2>Save as Test</h2>
                <div class="dialog-form">
                    <div class="form-group">
                        <label for="name">Name:</label>
                        <div id="nameContainer"></div>
                    </div>
                </div>
                <div class="dialog-buttons">
                    <button id="cancelButton" class="secondary-button">Cancel</button>
                    <button id="saveButton" class="primary-button">Save</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        document.getElementById('nameContainer').appendChild(nameInput);
        
        const cancelButton = document.getElementById('cancelButton');
        const saveButton = document.getElementById('saveButton');
        
        cancelButton.addEventListener('click', () => {
            document.body.removeChild(dialog);
        });
        
        saveButton.addEventListener('click', () => {
            const name = nameInput.value.trim();
            
            if (!name) {
                alert('Please enter a name');
                return;
            }
            
            vscode.postMessage({
                command: 'createTest',
                name,
                code,
                language
            });
            
            document.body.removeChild(dialog);
        });
    }
    
    // Render execute result
    function renderExecuteResult() {
        if (!executeResult) {
            executeResultSection.classList.add('hidden');
            return;
        }
        
        executeResultSection.classList.remove('hidden');
        executeResultStatus.textContent = executeResult.success ? 'Success' : 'Failed';
        executeResultStatus.className = executeResult.success ? 'success' : 'error';
        executeResultTime.textContent = executeResult.executionTime ? executeResult.executionTime.toString() : '0';
        executeResultOutput.textContent = executeResult.output || '';
        
        if (executeResult.error) {
            executeResultErrorSection.classList.remove('hidden');
            executeResultError.textContent = executeResult.error;
        } else {
            executeResultErrorSection.classList.add('hidden');
        }
    }
    
    // Format date
    function formatDate(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
})();
