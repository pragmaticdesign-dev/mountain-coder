// ============================================================================
// GLOBAL STATE
// ============================================================================

let editor;
let currentQuestionId = null;
let lastView = 'dashboard';
let boilerplates = {};

// ============================================================================
// CONSTANTS
// ============================================================================

const VIEWS = {
    DASHBOARD: 'view-dashboard',
    LIST: 'view-list',
    EDITOR: 'view-editor'
};

const TABS = {
    DESC: 'desc',
    HINTS: 'hints',
    SOL: 'sol',
    NOTES: 'notes'
};

const TOPICS = [
    'array', 'map', 'two_pointers', 'string', 
    'dp', 'tree', 'graph', 'binary_search',"maths",
    "recursion"
];

const DIFFICULTY_COLORS = {
    'Easy': '#4ec9b0',
    'Medium': '#ce9178',
    'Hard': '#f44747'
};

const STORAGE_KEYS = {
    SOLUTION: 'solution',
    NOTES: 'notes',
    SOLVED: 'solved_ids',
    ATTEMPTED: 'attempted_ids'
};

// ============================================================================
// INITIALIZATION
// ============================================================================

require.config({ paths: { 'vs': '/static/vs' } });

if (typeof marked !== 'undefined') {
    marked.use({ gfm: true, breaks: true });
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function renderMarkdown(text) {
    if (!text) return "<p style='color:#666;'>No solution available.</p>";
    try {
        return marked.parse(text);
    } catch (e) {
        return `<pre>${text}</pre>`;
    }
}

function getElement(id) {
    return document.getElementById(id);
}

function hideElement(id) {
    getElement(id).classList.add('hidden');
}

function showElement(id) {
    getElement(id).classList.remove('hidden');
}

// ============================================================================
// STORAGE MANAGEMENT
// ============================================================================

function buildStorageKey(type, problemId, language = null) {
    if (language) {
        return `${type}_${problemId}_${language}`;
    }
    return `${type}_${problemId}`;
}

function getStorageItem(key, defaultValue = null) {
    return localStorage.getItem(key) || defaultValue;
}

function setStorageItem(key, value) {
    localStorage.setItem(key, value);
}

function getStorageArray(key) {
    return JSON.parse(getStorageItem(key, '[]'));
}

function setStorageArray(key, array) {
    setStorageItem(key, JSON.stringify(array));
}

// ============================================================================
// CODE STORAGE
// ============================================================================

let saveTimer;

function saveCodeToLocal() {
    if (!editor || !currentQuestionId) return;
    
    const code = editor.getValue();
    const language = getElement('lang-select').value;
    const key = buildStorageKey(STORAGE_KEYS.SOLUTION, currentQuestionId, language);
    
    setStorageItem(key, code);
}

function triggerAutoSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveCodeToLocal, 1000);
}

function loadSavedCode(problemId, language) {
    const key = buildStorageKey(STORAGE_KEYS.SOLUTION, problemId, language);
    return getStorageItem(key);
}

function resetCodeToBoilerplate() {
    // 1. Safety Check: Ensure editor and data exist
    if (!editor || !currentQuestionId) {
        console.warn("Cannot reset: No active question or editor.");
        return;
    }

    // 2. Confirm action
    if (!confirm("⚠️ Reset code to default? This will lose your current changes.")) {
        return;
    }
    
    // 3. Get current language and boilerplate
    const language = getElement('lang-select').value;
    
    // Debugging: Check if boilerplates exist
    console.log("Attempting reset. Language:", language, "Available:", boilerplates);

    if (boilerplates && boilerplates[language] !== undefined) {
        // 4. Update Editor
        editor.setValue(boilerplates[language]);
        
        // 5. Save immediately so the reset persists on refresh
        saveCodeToLocal();
        
        // 6. Visual feedback
        updateOutput("Code reset to boilerplate.", "#cca700");
    } else {
        alert(`No boilerplate code found for ${language}.`);
    }
}

function initToolbarEvents() {
    // Bind Reset Button
    // Tries to find by ID 'btn-reset' or class '.btn-reset'
    const resetBtn = document.getElementById('btn-reset') || document.querySelector('.btn-reset');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetCodeToBoilerplate);
    } else {
        console.warn("Reset button not found in DOM");
    }

    // Bind Back Button
    const backBtn = document.querySelector('.btn-back');
    if (backBtn) {
        backBtn.addEventListener('click', goBackToList);
    }

    // Bind Run Button
    const runBtn = document.querySelector('.btn-run');
    if (runBtn) {
        runBtn.addEventListener('click', runCustom); // Or submitCode depending on your UI
    }
    
    // Bind Language Select Change
    const langSelect = getElement('lang-select');
    if (langSelect) {
        langSelect.addEventListener('change', changeLanguage);
    }
}

// ============================================================================
// NOTES MANAGEMENT
// ============================================================================

function loadNotes(problemId) {
    const key = buildStorageKey(STORAGE_KEYS.NOTES, problemId);
    const savedNotes = getStorageItem(key, '');
    getElement('notes-area').value = savedNotes;
}

function saveNotes(problemId, notes) {
    const key = buildStorageKey(STORAGE_KEYS.NOTES, problemId);
    setStorageItem(key, notes);
}

function initNotesAutoSave() {
    getElement('notes-area').addEventListener('input', (e) => {
        if (!currentQuestionId) return;
        saveNotes(currentQuestionId, e.target.value);
    });
}

// ============================================================================
// PROGRESS TRACKING
// ============================================================================

function addToProgressList(listKey, problemId) {
    const id = parseInt(problemId);
    const list = getStorageArray(listKey);
    
    if (!list.includes(id)) {
        list.push(id);
        setStorageArray(listKey, list);
    }
}

function removeFromProgressList(listKey, problemId) {
    const id = parseInt(problemId);
    const list = getStorageArray(listKey);
    const filtered = list.filter(item => item !== id);
    setStorageArray(listKey, filtered);
}

function isInProgressList(listKey, problemId) {
    const id = parseInt(problemId);
    const list = getStorageArray(listKey);
    return list.includes(id);
}

function markProblemAsSolved(problemId) {
    addToProgressList(STORAGE_KEYS.SOLVED, problemId);
    removeFromProgressList(STORAGE_KEYS.ATTEMPTED, problemId);
}

function markProblemAsAttempted(problemId) {
    if (isInProgressList(STORAGE_KEYS.SOLVED, problemId)) return;
    addToProgressList(STORAGE_KEYS.ATTEMPTED, problemId);
}

function getStatusIcon(problemId) {
    const id = parseInt(problemId);
    
    if (isInProgressList(STORAGE_KEYS.SOLVED, id)) {
        return '<span style="color:#4ec9b0; margin-right:5px;" title="Solved">✅</span>';
    }
    
    if (isInProgressList(STORAGE_KEYS.ATTEMPTED, id)) {
        return '<span style="color:#cca700; margin-right:5px;" title="Attempted">⚠️</span>';
    }
    
    return '';
}

// ============================================================================
// VIEW MANAGEMENT
// ============================================================================

function showView(viewId) {
    Object.values(VIEWS).forEach(id => hideElement(id));
    showElement(viewId);
}

function switchTab(tabName) {
    Object.values(TABS).forEach(tab => {
        hideElement(`tab-${tab}`);
        getElement(`btn-tab-${tab}`).classList.remove('active');
    });
    
    showElement(`tab-${tabName}`);
    getElement(`btn-tab-${tabName}`).classList.add('active');
}

function goBackToList() {
    if (lastView === 'dashboard') {
        loadDashboard();
    } else {
        showView(VIEWS.LIST);
    }
}

// ============================================================================
// UI RENDERING - DASHBOARD
// ============================================================================

function renderDashboardFilters() {
    const difficultyButtons = Object.keys(DIFFICULTY_COLORS)
        .map(diff => {
            const cssClass = `diff-${diff.toLowerCase().substring(0, 3)}`;
            return `<button onclick="filterByDifficulty('${diff}')" class="tag-pill ${cssClass}">${diff}</button>`;
        })
        .join('');
    
    const topicButtons = TOPICS
        .map(topic => `<button onclick="filterByTag('${topic}')" class="tag-pill topic">${topic}</button>`)
        .join('');
    
    return `
        <div class="filter-section">
            <div class="filter-group">
                <span class="filter-label">Difficulty:</span>
                ${difficultyButtons}
            </div>
            <div class="filter-group" style="margin-top:5px;">
                <span class="filter-label">Topics:</span>
                ${topicButtons}
                <button onclick="loadDashboard()" class="tag-pill clear">Reset</button>
            </div>
        </div>
    `;
}

function renderCard(card) {
    return `
        <div class="card" onclick="loadCardProblems(${card.id}, '${card.title}')">
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <h3 style="margin:0 0 10px 0; color:#fff;">${card.title}</h3>
                <span style="font-size:20px;">📚</span>
            </div>
            <p style="color:#aaa; font-size: 0.9em; margin-bottom: 20px; min-height:40px;">
                ${card.description || 'Master the basics with this curated list.'}
            </p>
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #3c3c3c; padding-top:10px;">
                <span class="badge" style="background:#333; color:#ccc; padding:4px 8px; border-radius:4px; font-size:12px;">
                    ${card.question_count} Problems
                </span>
                <span style="color:#0e639c; font-size:13px; font-weight:500;">Start →</span>
            </div>
        </div>
    `;
}

// ============================================================================
// UI RENDERING - PROBLEM LIST
// ============================================================================

function renderProblemRow(problem) {
    const diffColor = DIFFICULTY_COLORS[problem.difficulty] || '#ccc';
    const tags = (problem.tags || [])
        .map(tag => `<span class="tag-badge">${tag}</span>`)
        .join('');
    
    return `
        <tr style="cursor:pointer;" onclick="loadQuestion(${problem.id})">
            <td style="color:#666; font-family:monospace;">
                ${getStatusIcon(problem.id)} #${problem.id}
            </td>
            <td style="font-weight:500; color:#fff;">${problem.title}</td>
            <td>${tags}</td>
            <td style="color:${diffColor};">${problem.difficulty}</td>
            <td style="text-align:right;">
                <button class="btn-solve" style="color:${diffColor}; background:none; border:1px solid ${diffColor}; padding:2px 8px;">
                    Solve
                </button>
            </td>
        </tr>
    `;
}

function renderProblemsTable(problems) {
    const tbody = getElement('problems-tbody');
    
    if (!problems.length) {
        tbody.innerHTML = "<tr><td colspan='5' style='text-align:center; padding:20px;'>No problems found.</td></tr>";
        return;
    }
    
    tbody.innerHTML = problems.map(renderProblemRow).join('');
}

// ============================================================================
// UI RENDERING - QUESTION DETAILS
// ============================================================================

function renderQuestionHeader(data) {
    getElement('q-title').innerText = `${data.id}. ${data.title}`;
}

function renderQuestionDescription(data) {
    getElement('q-desc').innerHTML = marked.parse(data.description);
    
    if (window.MathJax) {
        MathJax.typesetPromise([getElement('q-desc')]);
    }
}

function renderQuestionFormats(data) {
    getElement('q-input-fmt').innerText = data.input_format || '';
    getElement('q-output-fmt').innerText = data.output_format || '';
}

function renderQuestionExamples(examples) {
    const formatted = (examples || [])
        .map((ex, i) => `Ex ${i + 1}:\nInput:\n${ex.input}\n\nOutput:\n${ex.output}`)
        .join('\n\n') || 'No examples.';
    
    getElement('q-examples').innerText = formatted;
}

function renderQuestionHints(hints) {
    const hintsList = hints && hints.length
        ? hints.map(hint => `<li>${hint}</li>`).join('')
        : "<li style='color:#666; list-style:none'>No hints.</li>";
    
    getElement('q-hints-list').innerHTML = hintsList;
}

function renderQuestionSolution(solution) {
    let content = renderMarkdown(solution);
    
    // NEW: Append solution image if it exists (hidden automatically if missing)
    if (currentQuestionId) {
        content += `
            <div class="solution-image-container">
                <img 
                    src="/images/${currentQuestionId}.png" 
                    class="solution-image" 
                    onerror="this.parentElement.style.display='none'"
                />
            </div>
        `;
    }

    getElement('q-solution').innerHTML = content;
}

// ============================================================================
// API CALLS
// ============================================================================

async function fetchJson(url) {
    const response = await fetch(url);
    return response.json();
}

async function postJson(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return response.json();
}

// ============================================================================
// DASHBOARD LOADING
// ============================================================================

async function loadDashboard() {
    lastView = 'dashboard';
    showView(VIEWS.DASHBOARD);
    
    const cards = await fetchJson('/questions/cards');
    
    getElement('dashboard-filters').innerHTML = renderDashboardFilters();
    getElement('cards-container').innerHTML = cards.map(renderCard).join('');
}

// ============================================================================
// PROBLEM LIST LOADING
// ============================================================================

async function loadCardProblems(cardId, title) {
    lastView = 'list';
    showView(VIEWS.LIST);
    
    getElement('list-title').innerText = title;
    
    const problems = await fetchJson(`/questions/cards/${cardId}/questions`);
    renderProblemsTable(problems);
}

async function filterByDifficulty(difficulty) {
    lastView = 'list';
    showView(VIEWS.LIST);
    
    getElement('list-title').innerText = `Difficulty: ${difficulty}`;
    
    const problems = await fetchJson(`/questions/search?difficulty=${difficulty}`);
    renderProblemsTable(problems);
}

async function filterByTag(tag) {
    lastView = 'list';
    showView(VIEWS.LIST);
    
    getElement('list-title').innerText = `Topic: ${tag}`;
    
    const problems = await fetchJson(`/questions/search?tag=${tag}`);
    renderProblemsTable(problems);
}

async function handleSearch(e) {
    if (e.key !== 'Enter') return;
    
    const query = getElement('search-input').value;
    
    if (!query.trim()) {
        return loadDashboard();
    }
    
    lastView = 'list';
    showView(VIEWS.LIST);
    
    getElement('list-title').innerText = `Search: "${query}"`;
    
    try {
        const problems = await fetchJson(`/questions/search?q=${query}`);
        renderProblemsTable(problems);
    } catch (e) {
        console.error('Search failed:', e);
    }
}

// ============================================================================
// QUESTION LOADING
// ============================================================================

async function loadQuestion(problemId) {
    currentQuestionId = problemId;
    showView(VIEWS.EDITOR);
    switchTab(TABS.DESC);
    loadNotes(problemId);
    
    try {
        const data = await fetchJson(`/questions/${problemId}`);
        
        renderQuestionHeader(data);
        renderQuestionDescription(data);
        renderQuestionFormats(data);
        renderQuestionExamples(data.examples);
        renderQuestionHints(data.hints);
        renderQuestionSolution(data.solution);
        
        boilerplates = data.boilerplate;
        
        const language = 'python';
        getElement('lang-select').value = language;
        
        const savedCode = loadSavedCode(problemId, language);
        const initialCode = savedCode || boilerplates[language];
        
        initEditor(initialCode, language);
        
    } catch (e) {
        alert('Error loading question');
        goBackToList();
    }
}

// ============================================================================
// MONACO EDITOR
// ============================================================================

function initEditor(code, language) {
    if (editor) {
        editor.setValue(code);
        monaco.editor.setModelLanguage(editor.getModel(), language);
    } else {
        require(['vs/editor/editor.main'], function() {
            editor = monaco.editor.create(getElement('monaco-editor'), {
                value: code,
                language: language,
                theme: 'vs-dark',
                automaticLayout: true,
                fontSize: 14,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                padding: { top: 10 },
                autoIndent: 'full',
                tabSize: 4,
                insertSpaces: true,
                wordBasedSuggestions: true,
                quickSuggestions: true
            });
            
            editor.onDidChangeModelContent(triggerAutoSave);
        });
    }
}

function changeLanguage() {
    const language = getElement('lang-select').value;
    const savedCode = loadSavedCode(currentQuestionId, language);
    const code = savedCode || (boilerplates ? boilerplates[language] : '');
    
    editor.setValue(code);
    monaco.editor.setModelLanguage(editor.getModel(), language);
}

// ============================================================================
// CODE EXECUTION
// ============================================================================

function updateOutput(text, color = '#ccc') {
    const output = getElement('output-text');
    output.innerText = text;
    output.style.color = color;
}

function formatSubmissionResult(result) {
    if (result.status === 'Accepted') {
        return {
            message: `✅ Accepted!\nTime: ${result.runtime}ms\nPassed: ${result.total_passed}/${result.total_tests}`,
            color: '#4ec9b0'
        };
    }
    
    let message = `❌ ${result.status}\nPassed: ${result.total_passed}/${result.total_tests}\n`;
    
    const failedCase = result.details.find(d => d.status === 'Fail');
    if (failedCase) {
        message += `\n[Case ${failedCase.test_case} Failed]\nExpected:\n${failedCase.expected}\nActual:\n${failedCase.actual}`;
    }
    
    return { message, color: '#f44747' };
}

async function submitCode() {
    if (!currentQuestionId || !editor) return;
    
    updateOutput('Running tests...');
    
    try {
        const result = await postJson('/submit', {
            question_id: currentQuestionId,
            language: getElement('lang-select').value,
            code: editor.getValue()
        });
        
        const { message, color } = formatSubmissionResult(result);
        updateOutput(message, color);
        
        if (result.status === 'Accepted') {
            markProblemAsSolved(currentQuestionId);
        } else {
            markProblemAsAttempted(currentQuestionId);
        }
        
    } catch (e) {
        updateOutput('Server Error', '#f44747');
    }
}

async function runCustom() {
    toggleConsole('output');
    updateOutput('Running...');
    
    try {
        const result = await postJson('/submit/run', {
            language: getElement('lang-select').value,
            code: editor.getValue(),
            input_data: getElement('custom-input-box').value
        });
        
        updateOutput(result.output, result.is_error ? '#f44747' : '#d4d4d4');
        
    } catch (e) {
        updateOutput('Error', '#f44747');
    }
}

// ============================================================================
// CONSOLE MANAGEMENT
// ============================================================================

function toggleConsole(mode) {
    const tabs = document.querySelectorAll('.panel-tab');
    
    if (mode === 'output') {
        showElement('console-output');
        hideElement('console-input');
        tabs[0].classList.add('active');
        tabs[1].classList.remove('active');
    } else {
        hideElement('console-output');
        showElement('console-input');
        tabs[0].classList.remove('active');
        tabs[1].classList.add('active');
    }
}

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        if (!getElement(VIEWS.EDITOR).classList.contains('hidden')) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                
                if (e.shiftKey) {
                    submitCode();
                } else {
                    runCustom();
                }
            }
        }
    });
}

// ============================================================================
// INITIALIZATION
// ============================================================================

initNotesAutoSave();
initKeyboardShortcuts();
initToolbarEvents();
loadDashboard();