let editor;
let currentQuestionId = null;
let boilerplates = {};

require.config({ paths: { 'vs': '/static/vs' } });

// 1. Load Dashboard
async function loadDashboard() {
    document.getElementById('view-dashboard').classList.remove('hidden');
    document.getElementById('view-editor').classList.add('hidden');
    
    const res = await fetch('/questions/cards');
    const cards = await res.json();
    
    const container = document.getElementById('cards-container');
    container.innerHTML = cards.map(c => `
        <div class="card">
            <h3>${c.title}</h3>
            <p>${c.description}</p>
            <hr style="border-color:#333; margin:10px 0;">
            ${c.questions.map(q => 
                `<div onclick="loadQuestion(${q.id})" style="padding:5px; cursor:pointer; color:#0e639c;">• ${q.title}</div>`
            ).join('')}
        </div>
    `).join('');
}

// 2. Load Question & Init Editor
async function loadQuestion(id) {
    currentQuestionId = id;
    document.getElementById('view-dashboard').classList.add('hidden');
    document.getElementById('view-editor').classList.remove('hidden');

    const res = await fetch(`/questions/${id}`);
    const data = await res.json();

    document.getElementById('q-title').innerText = data.title;
    document.getElementById('q-desc').innerText = data.description;
    document.getElementById('q-hints').innerHTML = data.hints.map(h => `<li>${h}</li>`).join('');
    document.getElementById('q-examples').innerHTML = data.examples.map(e => `Input: ${e.input}\nOutput: ${e.output}`).join('\n\n');

    boilerplates = data.boilerplate;
    
    // Init Monaco if not exists
    if (!editor) {
        require(['vs/editor/editor.main'], function() {
            editor = monaco.editor.create(document.getElementById('monaco-editor'), {
                value: boilerplates.python,
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true
            });
        });
    } else {
        editor.setValue(boilerplates.python);
        monaco.editor.setModelLanguage(editor.getModel(), 'python');
    }
}

// 3. Change Language
function changeLanguage() {
    const lang = document.getElementById('lang-select').value;
    editor.setValue(boilerplates[lang]);
    monaco.editor.setModelLanguage(editor.getModel(), lang);
}

// 4. Submit Code
async function submitCode() {
    const code = editor.getValue();
    const lang = document.getElementById('lang-select').value;
    const outputDiv = document.getElementById('output-panel');
    
    outputDiv.innerText = "Running tests...";
    
    try {
        const res = await fetch('/submit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ question_id: currentQuestionId, language: lang, code: code })
        });
        
        const result = await res.json();
        
        if (result.status === "Accepted") {
            outputDiv.style.color = "#4ec9b0";
            outputDiv.innerText = `✅ Accepted! Runtime: ${result.runtime}ms\nPassed ${result.total_passed}/${result.total_tests} tests.`;
        } else {
            outputDiv.style.color = "#f44747";
            const failDetail = result.details.find(d => d.status === "Fail");
            outputDiv.innerText = `❌ ${result.status}\nPassed: ${result.total_passed}/${result.total_tests}\n\nFailed Case:\nExpected: ${failDetail.expected}\nActual: ${failDetail.actual}`;
        }
    } catch (e) {
        outputDiv.innerText = "Error submitting code.";
    }
}

// Start
loadDashboard();