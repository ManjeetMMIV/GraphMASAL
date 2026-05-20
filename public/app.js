/* ============================================================
   GraphMASAL — App JS
   ============================================================ */

// ------------------------------------------------------------------ //
// State
// ------------------------------------------------------------------ //
const state = {
    studentId: '',
    topic: '',
    sessionId: null,
    chatHistory: [],
    isProcessing: false,
    activeSessions: [],
    teacherId: '',
    monitoredStudents: [],
    selectedStudentId: '',
};

// ------------------------------------------------------------------ //
// DOM References
// ------------------------------------------------------------------ //
const onboardingOverlay = document.getElementById('onboardingOverlay');
const appShell          = document.getElementById('appShell');
const onboardingForm    = document.getElementById('onboardingForm');
const onboardStudentId  = document.getElementById('onboardStudentId');
const onboardTopic      = document.getElementById('onboardTopic');
const startBtn          = document.getElementById('startBtn');

const headerTopic       = document.getElementById('headerTopic');
const sidebarStudentId  = document.getElementById('sidebarStudentId');
const sessionList       = document.getElementById('sessionList');
const refreshSessionsBtn= document.getElementById('refreshSessionsBtn');
const newChatBtn        = document.getElementById('newChatBtn');

const chatContainer     = document.getElementById('chatContainer');
const chatForm          = document.getElementById('chatForm');
const chatInput         = document.getElementById('chatInput');
const sendBtn           = document.getElementById('sendBtn');

const tracePanel        = document.getElementById('tracePanel');
const traceLogs         = document.getElementById('traceLogs');
const toggleTraceBtn    = document.getElementById('toggleTraceBtn');
const closeTraceBtn     = document.getElementById('closeTraceBtn');

const agentPipeline     = document.getElementById('agentPipeline');
const dropZone          = document.getElementById('dropZone');
const pdfUpload         = document.getElementById('pdfUpload');
const uploadStatus      = document.getElementById('uploadStatus');
const documentList      = document.getElementById('documentList');
const refreshDocsBtn    = document.getElementById('refreshDocsBtn');
const extractConceptsBtn= document.getElementById('extractConceptsBtn');

const showRoadmapBtn    = document.getElementById('showRoadmapBtn');
const resetDataBtn      = document.getElementById('resetDataBtn');
const roadmapModal      = document.getElementById('roadmapModal');
const closeRoadmapModal = document.getElementById('closeRoadmapModal');
const mermaidContainer  = document.getElementById('mermaidContainer');
const roadmapMeta       = document.getElementById('roadmapMeta');

// ------------------------------------------------------------------ //
// Init
// ------------------------------------------------------------------ //
mermaid.initialize({ startOnLoad: false, theme: 'base' });

// ------------------------------------------------------------------ //
// Utilities
// ------------------------------------------------------------------ //
function uuidv4() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = Math.random() * 16 | 0;
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
}

function timeAgo(isoStr) {
    if (!isoStr) return '';
    const diff = Date.now() - new Date(isoStr).getTime();
    const m = Math.floor(diff / 60000);
    const h = Math.floor(m / 60);
    const d = Math.floor(h / 24);
    if (d > 0) return `${d}d ago`;
    if (h > 0) return `${h}h ago`;
    if (m > 0) return `${m}m ago`;
    return 'just now';
}

function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ------------------------------------------------------------------ //
// Onboarding
// ------------------------------------------------------------------ //
onboardingForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const studentId = onboardStudentId.value.trim();
    const topic     = onboardTopic.value.trim();
    if (!studentId || !topic) return;

    startBtn.disabled = true;
    startBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Starting…';

    try {
        // 1. Create session
        const res = await fetch('/api/sessions/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: studentId, topic }),
        });
        if (!res.ok) throw new Error('Session creation failed');
        const session = await res.json();

        state.studentId = studentId;
        state.topic = topic;
        state.sessionId = session.session_id;
        state.chatHistory = [];

        // 2. Launch the app directly — the user can choose a learning plan when they're ready
        launchApp();
        addWelcomeMessage(topic);
        loadSessions();
        loadDocuments();

    } catch (err) {
        startBtn.disabled = false;
        startBtn.innerHTML = '<i class="fa-solid fa-rocket"></i> Start Learning';
        alert('Could not connect to backend. Is the server running?');
    }
});

// ------------------------------------------------------------------ //
// Source / Sink Selection Modal
// ------------------------------------------------------------------ //
function showSourceSinkModal(concepts) {
    const listHtml = concepts.length > 0
        ? concepts.map(c => `
        <div style="background:#fffcf7; border:1px solid #e5ddd0; border-radius:12px; padding:12px; margin-bottom:8px; display:flex; gap:12px; align-items:start;">
            <div style="flex:1">
                <div style="font-weight:600; font-size:0.95rem; color:#334155; margin-bottom:4px;">${c.name}</div>
                <div style="font-size:0.75rem; color:#64748b; line-height:1.4;">${escapeHtml(c.desc || '')}</div>
            </div>
            <div style="display:flex; flex-direction:column; gap:8px; align-items:flex-end;">
                <label style="font-size:0.7rem; color:#10b981; display:flex; align-items:center; gap:4px; cursor:pointer;">
                    <input type="checkbox" name="source" value="${c.id}" class="accent-emerald-500"> I know this
                </label>
                <label style="font-size:0.7rem; color:#6366f1; display:flex; align-items:center; gap:4px; cursor:pointer;">
                    <input type="checkbox" name="sink" value="${c.id}" class="accent-indigo-500"> I want to learn this
                </label>
            </div>
        </div>
    `).join('')
        : `<div style="text-align:center; padding:48px 16px; color:#64748b;">
            <i class="fa-solid fa-file-arrow-up" style="font-size:2.5rem; margin-bottom:16px; display:block; color:#475569;"></i>
            <div style="font-size:1rem; font-weight:600; color:#94a3b8; margin-bottom:8px;">No concepts extracted yet</div>
            <div style="font-size:0.85rem; line-height:1.6;">Upload a PDF from the Knowledge Base panel on the right,<br>then click the 🧠 brain button to extract concepts,<br>and come back here to choose your learning path.</div>
        </div>`;

    const modal = document.createElement('div');
    modal.id = 'planSelectModal';
    modal.style.cssText = `
        position:fixed; inset:0; background:rgba(51,65,85,0.45); z-index:9999;
        display:flex; align-items:center; justify-content:center; backdrop-filter:blur(6px);`;

    modal.innerHTML = `
        <div style="background:#fffcf7; border:1px solid #e5ddd0; border-radius:24px; width:90%; max-width:800px; max-height:85vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 25px 50px -12px rgba(79,70,229,0.12);">
            <div style="padding:24px 32px; border-bottom:1px solid #e5ddd0; background:#f7f4ef;">
                <h2 style="margin:0 0 8px; font-size:1.5rem; color:#1e293b; display:flex; align-items:center; gap:12px;">
                    <i class="fa-solid fa-route text-indigo-600"></i> Customize Your Path
                </h2>
                <p style="margin:0; font-size:0.9rem; color:#64748b;">
                    Select what you already know (sources) and what you want to achieve (targets). We'll compute the optimal route.
                </p>
            </div>

            <div style="padding:24px 32px; overflow-y:auto; flex:1;" class="custom-scrollbar">
                ${listHtml}
            </div>

            <div style="padding:24px 32px; border-top:1px solid #e5ddd0; background:#f7f4ef; display:flex; justify-content:space-between; align-items:center;">
                <button id="skipBtn" style="background:transparent; color:#64748b; border:1px solid #e5ddd0; padding:10px 20px; border-radius:10px; cursor:pointer; font-weight:500; transition:all 0.2s;">
                    Skip (Default Path)
                </button>
                <button id="computeBtn" style="background:#6366f1; color:white; border:none; padding:10px 24px; border-radius:10px; cursor:pointer; font-weight:600; display:flex; align-items:center; gap:8px; box-shadow:0 4px 14px 0 rgba(99,102,241,0.39); transition:all 0.2s;">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> Compute Optimal Path
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    const computeBtn = modal.querySelector('#computeBtn');
    const skipBtn = modal.querySelector('#skipBtn');

    // Make mutually exclusive per concept
    modal.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', (e) => {
            if (e.target.checked) {
                const row = e.target.closest('div').parentElement;
                const other = e.target.name === 'source' ? 'sink' : 'source';
                const otherCb = row.querySelector(`input[name="${other}"]`);
                if (otherCb) otherCb.checked = false;
            }
        });
    });

    const finalizePath = async (sources, sinks) => {
        computeBtn.disabled = true;
        computeBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Computing...';

        try {
            // 1. Run MSMS
            const msmsRes = await fetch('/api/compute_path', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_id: state.studentId,
                    source_ids: sources,
                    sink_ids: sinks
                })
            });
            const pathData = await msmsRes.json();
            const conceptSequence = pathData.path || [];

            // 2. Save Plan to Session
            await fetch('/api/select_plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_id: state.studentId,
                    session_id: state.sessionId,
                    plan_id: 'custom_path',
                    concept_sequence: conceptSequence,
                }),
            });
            
            if (conceptSequence.length > 0) {
                alert(`✅ Optimal path generated! ${conceptSequence.length} concepts to learn.\nPath:\n` + pathData.path_names.join(' → '));
            } else {
                alert(`ℹ️ Pathing returned no concepts. ${pathData.message || ''}`);
            }

        } catch (err) {
            console.error(err);
            alert("Error computing path.");
        }

        modal.remove();
        launchApp();
        addWelcomeMessage(state.topic);
        loadSessions();
        loadDocuments();
    };

    computeBtn.addEventListener('click', () => {
        const sources = Array.from(modal.querySelectorAll('input[name="source"]:checked')).map(cb => cb.value);
        const sinks = Array.from(modal.querySelectorAll('input[name="sink"]:checked')).map(cb => cb.value);
        finalizePath(sources, sinks);
    });

    skipBtn.addEventListener('click', () => {
        // Empty sources/sinks will fall back to default start/end nodes in the backend
        finalizePath([], []);
    });
}


function launchApp() {
    // Animate onboarding out
    onboardingOverlay.classList.add('fade-out');
    setTimeout(() => {
        onboardingOverlay.classList.add('hidden');
        appShell.classList.remove('hidden');
        appShell.classList.add('flex');
    }, 380);

    headerTopic.textContent = state.topic;
    sidebarStudentId.textContent = state.studentId;
    chatInput.focus();
}

// ------------------------------------------------------------------ //
// New Chat
// ------------------------------------------------------------------ //
async function startNewChat() {
    const topic = prompt('What topic do you want to study now?', state.topic);
    if (!topic || !topic.trim()) return;

    try {
        const res = await fetch('/api/sessions/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: state.studentId, topic: topic.trim() }),
        });
        const session = await res.json();
        state.sessionId = session.session_id;
        state.topic = topic.trim();
        state.chatHistory = [];

        headerTopic.textContent = state.topic;
        clearChat();
        addWelcomeMessage(state.topic);
        loadSessions();
        resetAgentBar();
    } catch (err) {
        alert('Failed to create new session.');
    }
}

newChatBtn.addEventListener('click', startNewChat);

// ------------------------------------------------------------------ //
// Welcome Message
// ------------------------------------------------------------------ //
function addWelcomeMessage(topic) {
    const content = `👋 Welcome! I'm your AI tutor for **${topic}**.

I'll start by checking what you already know, plan the best learning path for you, and then teach you step by step.

Your conversation history for this topic will be saved automatically — you can return anytime and pick up right where you left off.

**Ask me your first question, or just say "Let's begin!" to start.**`;
    appendMessage('assistant', content);
}

// ------------------------------------------------------------------ //
// Session Sidebar
// ------------------------------------------------------------------ //
async function loadSessions() {
    if (!state.studentId) return;
    try {
        const res = await fetch(`/api/sessions?student_id=${encodeURIComponent(state.studentId)}`);
        const data = await res.json();
        renderSessionList(data.sessions || []);
    } catch (err) {
        console.warn('Failed to load sessions', err);
    }
}

function renderSessionList(sessions) {
    if (!sessions.length) {
        sessionList.innerHTML = `
            <div class="text-center text-slate-500 text-xs py-8">
                <i class="fa-solid fa-comment-slash text-2xl mb-2 block"></i>
                No past sessions yet
            </div>`;
        return;
    }

    sessionList.innerHTML = sessions.map(s => `
        <div class="session-item group ${s.session_id === state.sessionId ? 'active' : ''}"
             data-id="${s.session_id}" onclick="loadSession('${s.session_id}','${escapeHtml(s.topic || '')}')">
            <div class="flex items-center justify-between gap-2 mb-0.5">
                <div class="flex items-center gap-1.5 min-w-0 flex-1">
                    <i class="fa-solid fa-book text-indigo-500 text-[9px] flex-shrink-0"></i>
                    <span class="session-topic truncate">${escapeHtml(s.topic || 'Untitled')}</span>
                </div>
                <button onclick="event.stopPropagation(); deleteSession('${s.session_id}')" class="delete-session-btn opacity-60 hover:opacity-100 text-red-500 hover:text-red-600 px-2 py-1 rounded flex-shrink-0 transition-all hover:bg-red-50" title="Delete conversation">
                    <i class="fa-solid fa-trash-can text-sm"></i>
                </button>
            </div>
            <div class="session-meta flex gap-2">
                <span>${s.turn_count || 0} turns</span>
                <span>·</span>
                <span>${timeAgo(s.updated_at || s.created_at)}</span>
            </div>
        </div>
    `).join('');
}

async function deleteSession(sessionId) {
    if (!confirm('Are you sure you want to delete this conversation? This cannot be undone.')) return;


    try {
        const res = await fetch(`/api/session/${sessionId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Failed to delete session');

        if (state.sessionId === sessionId) {
            state.sessionId = null;
            state.topic = '';
            state.chatHistory = [];
            document.getElementById('headerTopic').textContent = 'No active session';
            clearChat();
        }
        
        loadSessions();
    } catch (err) {
        console.error(err);
        alert('Failed to delete session.');
    }
}

async function loadSession(sessionId, topic) {
    if (sessionId === state.sessionId && !confirm('Reload this session from history?')) return;

    try {
        const res = await fetch(`/api/session/${sessionId}`);
        const data = await res.json();

        state.sessionId = sessionId;
        state.topic = topic || data.info?.topic || '';
        state.chatHistory = data.history || [];

        headerTopic.textContent = state.topic;
        clearChat();
        resetAgentBar();

        // Replay history into chat window
        if (!data.history || data.history.length === 0) {
            addWelcomeMessage(state.topic);
        } else {
            for (const msg of data.history) {
                if (msg.content) appendMessage(msg.role, msg.content);
            }
        }

        // Highlight active session
        document.querySelectorAll('.session-item').forEach(el => {
            el.classList.toggle('active', el.dataset.id === sessionId);
        });
    } catch (err) {
        alert('Failed to load session.');
    }
}

refreshSessionsBtn.addEventListener('click', loadSessions);

// ------------------------------------------------------------------ //
// Chat
// ------------------------------------------------------------------ //
function clearChat() {
    chatContainer.innerHTML = '';
    traceLogs.innerHTML = '';
    toggleTraceBtn.classList.add('hidden');
    tracePanel.classList.add('hidden');
}

function appendMessage(role, content) {
    const div = document.createElement('div');
    div.className = 'flex gap-3 message-appear';

    if (role === 'user') {
        div.classList.add('flex-row-reverse');
        div.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-card border border-border flex-shrink-0 flex items-center justify-center text-slate-500 text-xs mt-0.5">
                <i class="fa-regular fa-user"></i>
            </div>
            <div class="bg-primary/90 text-white rounded-2xl rounded-tr-none px-4 py-3 max-w-[80%] text-sm leading-relaxed shadow-md chat-bubble">
                ${marked.parse(content)}
            </div>`;
    } else {
        div.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex-shrink-0 flex items-center justify-center text-white text-xs mt-0.5 shadow-md shadow-primary/30">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="bg-card border border-border rounded-2xl rounded-tl-none px-4 py-3 max-w-[80%] text-sm leading-relaxed text-slate-800 shadow-sm chat-bubble">
                ${content ? marked.parse(content) : typingDots()}
            </div>`;
    }

    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return div;
}

function typingDots() {
    return `<div id="typingIndicator" class="flex flex-col gap-1.5 justify-center">
        <div class="flex items-center gap-1 h-3">
            <div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>
        </div>
        <span class="status-text text-[10px] text-slate-500 italic font-semibold">Getting ready to help you…</span>
    </div>`;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text || state.isProcessing) return;
    if (!state.sessionId) { alert('No active session. Please reload.'); return; }

    appendMessage('user', text);
    chatInput.value = '';
    toggleTraceBtn.classList.remove('hidden');

    // Placeholder assistant bubble
    const assistantDiv = appendMessage('assistant', '');
    const bubbleContent = assistantDiv.querySelector('.chat-bubble');

    state.isProcessing = true;
    chatInput.disabled = true;
    sendBtn.disabled = true;
    updateAgentBar('router');

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: state.sessionId,
                student_id: state.studentId,
                topic: state.topic,
                message: text,
                chat_history: state.chatHistory,
            }),
        });

        if (!res.ok) throw new Error('API error');

        const reader = res.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let fullResponse = '';
        bubbleContent.innerHTML = ''; // strip typing dots

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                if (!line.startsWith('event: ')) continue;

                const eventType = line.substring(7).trim();
                const dataLine = lines[i + 1];
                if (!dataLine?.startsWith('data: ')) continue;
                const dataStr = dataLine.substring(6).trim();

                if (eventType === 'node_update') {
                    const data = JSON.parse(dataStr);
                    updateAgentBar(data.node.toLowerCase());
                    appendTraceEntry(data.node, data.state);

                } else if (eventType === 'message') {
                    const data = JSON.parse(dataStr);
                    fullResponse = data.content;
                    bubbleContent.innerHTML = marked.parse(fullResponse);
                    chatContainer.scrollTop = chatContainer.scrollHeight;

                } else if (eventType === 'done') {
                    resetAgentBar();

                } else if (eventType === 'error') {
                    bubbleContent.innerHTML = `<span class="text-red-400">Error: ${JSON.parse(dataStr).detail}</span>`;
                    resetAgentBar();
                }

                i++; // skip data line
            }
        }

        // Commit to local history
        state.chatHistory.push({ role: 'user', content: text });
        state.chatHistory.push({ role: 'assistant', content: fullResponse || 'Workflow completed.' });

        if (!fullResponse) {
            bubbleContent.innerHTML = marked.parse('Workflow completed with no specific output.');
        }

        // Refresh sidebar to update turn count
        loadSessions();

    } catch (err) {
        bubbleContent.innerHTML = `<span class="text-red-400">Connection error. Is the server running?</span>`;
        resetAgentBar();
    } finally {
        state.isProcessing = false;
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
});

// ------------------------------------------------------------------ //
// Agent Bar
// ------------------------------------------------------------------ //
const AGENT_ORDER = ['router', 'diagnoser', 'planner', 'tutor'];
const FRIENDLY_STATUSES = {
    'router': 'Understanding your question…',
    'diagnoser': 'Checking what you already know…',
    'planner': 'Planning the best way to teach this…',
    'tutor': 'Preparing your answer…',
};

function updateAgentBar(activeNode) {
    const nodeKey = (activeNode || '').toLowerCase();
    const chips = agentPipeline.querySelectorAll('.agent-chip');
    let foundActive = false;
    chips.forEach(chip => {
        const name = chip.dataset.agent;
        chip.classList.remove('active', 'done');
        if (name === nodeKey) {
            chip.classList.add('active');
            foundActive = true;
        } else if (!foundActive) {
            chip.classList.add('done');
        }
    });

    const statusTextEl = document.querySelector('#typingIndicator .status-text');
    if (statusTextEl) {
        statusTextEl.textContent = FRIENDLY_STATUSES[nodeKey] || 'Almost there…';
    }
}

function resetAgentBar() {
    agentPipeline.querySelectorAll('.agent-chip').forEach(c => c.classList.remove('active', 'done'));
}

// ------------------------------------------------------------------ //
// Trace Panel
// ------------------------------------------------------------------ //
function appendTraceEntry(node, stateObj) {
    const div = document.createElement('div');
    div.className = 'flex gap-1.5';
    div.innerHTML = `
        <span class="text-indigo-400 font-bold flex-shrink-0">[${node}]</span>
        <span class="text-gray-500 break-all">${JSON.stringify(stateObj)}</span>`;
    traceLogs.appendChild(div);
    traceLogs.scrollTop = traceLogs.scrollHeight;
}

toggleTraceBtn.addEventListener('click', () => {
    tracePanel.classList.remove('hidden');
});
closeTraceBtn.addEventListener('click', () => {
    tracePanel.classList.add('hidden');
});

// ------------------------------------------------------------------ //
// PDF Upload
// ------------------------------------------------------------------ //
dropZone.addEventListener('click', () => pdfUpload.click());
dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('border-primary/50'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('border-primary/50'));
dropZone.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-primary/50');
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') await uploadFile(file);
});

pdfUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) await uploadFile(file);
});

async function uploadFile(file) {
    uploadStatus.classList.remove('hidden');
    uploadStatus.innerHTML = `
        <div class="h-1 w-full bg-border rounded-full overflow-hidden">
            <div class="h-full bg-primary animate-pulse w-full rounded-full"></div>
        </div>
        <p class="text-[10px] text-center text-primary mt-1">Ingesting PDF…</p>`;

        const formData = new FormData();
        const stdId = window.studentId || state.studentId || 'default-student';
        formData.append('student_id', stdId);
        formData.append('file', file);

        try {
            const res = await fetch('/api/upload_pdf', { method: 'POST', body: formData });
            const data = await res.json();

        if (res.ok) {
            uploadStatus.innerHTML = `<p class="text-[10px] text-center text-emerald-400 font-medium mt-1">
                <i class="fa-solid fa-check mr-1"></i>${data.chunk_count} chunks + ${data.concept_count ?? 0} concepts added from "${data.file_name}"
            </p>`;
            loadDocuments();
        } else {
            uploadStatus.innerHTML = `<p class="text-[10px] text-center text-red-400 mt-1">Error: ${data.detail}</p>`;
        }
    } catch (err) {
        uploadStatus.innerHTML = `<p class="text-[10px] text-center text-red-400 mt-1">Network Error</p>`;
    }

    setTimeout(() => uploadStatus.classList.add('hidden'), 6000);
    pdfUpload.value = '';
}

// ------------------------------------------------------------------ //
// Document List
// ------------------------------------------------------------------ //
async function loadDocuments() {
    try {
        const stdId = window.studentId || state.studentId || 'default-student';
        const res = await fetch(`/api/documents?student_id=${encodeURIComponent(stdId)}`);
        const data = await res.json();
        renderDocumentList(data.documents || []);
    } catch (err) {
        console.warn('Failed to load documents', err);
    }
}

function renderDocumentList(docs) {
    if (!docs.length) {
        documentList.innerHTML = `
            <div class="text-center text-gray-600 text-xs py-8">
                <i class="fa-solid fa-file-pdf text-2xl mb-2 block"></i>
                No documents uploaded
            </div>`;
        return;
    }

    documentList.innerHTML = docs.map(d => `
        <div class="doc-item">
            <i class="fa-solid fa-file-pdf text-red-500 text-xs flex-shrink-0"></i>
            <span class="doc-name" title="${escapeHtml(d.file_name)}">${escapeHtml(d.file_name)}</span>
            <span class="doc-chunks">${d.chunk_count} chunks</span>
        </div>
    `).join('');
}

refreshDocsBtn.addEventListener('click', loadDocuments);

// ------------------------------------------------------------------ //
// Extract Concepts (Backfill)
// ------------------------------------------------------------------ //
if (extractConceptsBtn) {
    extractConceptsBtn.addEventListener('click', async () => {
        const orig = extractConceptsBtn.innerHTML;
        extractConceptsBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-xs"></i>';
        extractConceptsBtn.disabled = true;
        try {
            const stdId = window.studentId || state.studentId || 'default-student';
            const res = await fetch('/api/extract_concepts', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ student_id: stdId })
            });
            const data = await res.json();
            if (res.ok) {
                alert(`✅ Extracted ${data.total_concepts} concepts from ${(data.documents||[]).length} document(s). You can now use \'Start Learning\' to get a plan!`);
            } else {
                alert(`Error: ${data.detail}`);
            }
        } catch (err) {
            alert('Failed to extract concepts: ' + err.message);
        } finally {
            extractConceptsBtn.innerHTML = orig;
            extractConceptsBtn.disabled = false;
        }
    });
}

const choosePlanBtn = document.getElementById('choosePlanBtn');
const clearDocsBtn  = document.getElementById('clearDocsBtn');

// ------------------------------------------------------------------ //
// Choose Plan (from inside active chat)
// ------------------------------------------------------------------ //
if (choosePlanBtn) {
    choosePlanBtn.addEventListener('click', async () => {
        if (!state.studentId) {
            alert('Please start a session first.');
            return;
        }
        choosePlanBtn.disabled = true;
        choosePlanBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Loading…';
        try {
            // First, auto-extract concepts using the correct studentId
            await fetch('/api/extract_concepts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ student_id: state.studentId })
            });
            const res = await fetch(`/api/concepts?student_id=${encodeURIComponent(state.studentId)}`);
            const data = await res.json();
            const concepts = data.concepts || [];
            // Always show the modal — if no concepts, it shows a helpful message inside
            showSourceSinkModal(concepts);
        } catch (err) {
            showSourceSinkModal([]);  // show empty modal with message
        } finally {
            choosePlanBtn.disabled = false;
            choosePlanBtn.innerHTML = '<i class="fa-solid fa-map-marked-alt"></i> Choose Learning Plan';
        }
    });
}


// ------------------------------------------------------------------ //
// Reset
// ------------------------------------------------------------------ //
resetDataBtn.addEventListener('click', async () => {
    if (!confirm(`Reset all data for "${state.studentId}"? This cannot be undone.`)) return;
    try {
        const res = await fetch('/api/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: state.studentId }),
        });
        if (res.ok) {
            alert('All student data cleared. Starting fresh!');
            clearChat();
            state.chatHistory = [];
            loadSessions();
            loadDocuments();
            addWelcomeMessage(state.topic);
        }
    } catch (err) {
        alert('Failed to reset data.');
    }
});

clearDocsBtn.addEventListener('click', async () => {
    const stdId = window.studentId || state.studentId || 'default-student';
    if (!confirm(`Delete ALL uploaded documents for student "${stdId}" from Neo4j? This cannot be undone.`)) return;
    clearDocsBtn.disabled = true;
    clearDocsBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin mr-1"></i> Deleting…';
    try {
        const res = await fetch(`/api/documents?student_id=${encodeURIComponent(stdId)}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok) {
            loadDocuments();
            alert(`Done! Removed all PDF documents for "${stdId}" from the knowledge base.`);
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (err) {
        alert('Network error.');
    } finally {
        clearDocsBtn.disabled = false;
        clearDocsBtn.innerHTML = '<i class="fa-solid fa-file-circle-xmark mr-1"></i> Clear All Documents';
    }
});

// ------------------------------------------------------------------ //
// Roadmap (vis.js interactive network graph)
// ------------------------------------------------------------------ //
function showRoadmap() {
    roadmapMeta.textContent = 'Fetching knowledge graph…';
    mermaidContainer.innerHTML = `
        <div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:16px;">
            <i class="fa-solid fa-circle-notch fa-spin" style="font-size:2.5rem;color:#6366f1;"></i>
            <div style="color:#94a3b8;font-size:0.9rem;">Building your knowledge graph…</div>
        </div>`;
    roadmapModal.classList.remove('opacity-0', 'pointer-events-none');
    roadmapModal.firstElementChild.classList.remove('scale-95');

    if (!state.studentId || !state.sessionId) {
        roadmapMeta.textContent = 'No active session.';
        mermaidContainer.innerHTML = `<div style="text-align:center;padding:80px 20px;color:#64748b;">Please start a learning session first.</div>`;
        return;
    }

    fetch(`/api/knowledge_graph?student_id=${encodeURIComponent(state.studentId)}&session_id=${encodeURIComponent(state.sessionId)}`)
        .then(r => r.json())
        .then(data => {
            const allNodes = data.nodes || [];
            const allEdges = data.edges || [];
            const activePlan = data.active_plan || [];
            const currentConcept = data.current_concept || null;
            const justification = data.justification || null;

            if (allNodes.length === 0) {
                roadmapMeta.textContent = 'No concepts extracted yet.';
                mermaidContainer.innerHTML = `
                    <div style="text-align:center;padding:80px 20px;color:#64748b;">
                        <i class="fa-solid fa-diagram-project" style="font-size:2.5rem;margin-bottom:16px;display:block;color:#334155;"></i>
                        No knowledge graph available yet.<br>Upload a PDF and extract concepts first.
                    </div>`;
                return;
            }

            const activeSet = new Set(activePlan);
            const activeIndex = {};
            activePlan.forEach((id, i) => { activeIndex[id] = i; });

            // --- 4-State Node Coloring ---
            // MASTERED  (score >= 0.8): Green — done ✅
            // CURRENT   (first unmastered in plan): Amber/Gold — learning now 🎯
            // UPCOMING  (in plan, after current): Indigo — queued 🔵
            // OFF-PLAN  (not in active plan): Light gray ⚪
            const stateColors = {
                mastered:  { bg: '#d1fae5', border: '#10b981', font: '#065f46', shadow: '#10b98144' },
                current:   { bg: '#fef3c7', border: '#f59e0b', font: '#92400e', shadow: '#f59e0b55' },
                upcoming:  { bg: '#ede9fe', border: '#6366f1', font: '#3730a3', shadow: '#6366f144' },
                offplan:   { bg: '#f8fafc', border: '#cbd5e1', font: '#64748b', shadow: null },
            };

            function getNodeState(n) {
                if (!activeSet.has(n.id)) return 'offplan';
                if (n.mastery >= 0.8) return 'mastered';
                if (n.id === currentConcept) return 'current';
                return 'upcoming';
            }

            const visNodes = allNodes.map(n => {
                const nodeState = getNodeState(n);
                const c = stateColors[nodeState];
                const idx = activeIndex[n.id] ?? -1;
                const label = n.name.length > 22 ? n.name.slice(0, 20) + '…' : n.name;
                const stepLabel = idx >= 0 ? `\n#${idx + 1}` : '';

                const masteryPct = Math.round((n.mastery || 0) * 100);
                const stateLabel = nodeState === 'mastered' ? '✅ Mastered'
                    : nodeState === 'current'  ? '🎯 Currently Learning'
                    : nodeState === 'upcoming' ? '🔵 Upcoming'
                    : '⚪ Related';

                const plainTitle = `${n.name}\n${stateLabel} · Mastery: ${masteryPct}%\n\n${n.desc || 'No description available.'}`;

                return {
                    id: n.id,
                    label: label + (idx >= 0 ? stepLabel : ''),
                    title: plainTitle,
                    color: {
                        background: c.bg,
                        border: c.border,
                        highlight: { background: c.bg, border: c.border },
                        hover:      { background: c.bg, border: c.border }
                    },
                    font: { color: c.font, size: nodeState === 'current' ? 15 : 12, bold: nodeState === 'current' },
                    borderWidth: nodeState === 'current' ? 3 : (nodeState !== 'offplan' ? 2 : 1),
                    size: nodeState === 'current' ? 32 : (nodeState !== 'offplan' ? 26 : 20),
                    shape: 'box',
                    margin: 10,
                    shadow: c.shadow ? { enabled: true, color: c.shadow, size: 14 } : false,
                };
            });

            // Build vis dataset edges
            const visEdges = allEdges.map((e, i) => {
                const bothActive = activeSet.has(e.source) && activeSet.has(e.target);
                return {
                    id: i,
                    from: e.source,
                    to: e.target,
                    color: {
                        color: bothActive ? '#6366f1' : '#e2e8f0',
                        highlight: '#6366f1',
                        opacity: bothActive ? 1 : 0.5,
                    },
                    width: bothActive ? 2.5 : 1,
                    arrows: { to: { enabled: true, scaleFactor: bothActive ? 0.8 : 0.5 } },
                    smooth: { type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.4 },
                    shadow: bothActive ? { enabled: true, color: '#6366f133', size: 6 } : false,
                };
            });

            // Add sequential dashed edges along path for gaps not in prerequisite list
            const edgeKeys = new Set(allEdges.map(e => `${e.source}→${e.target}`));
            activePlan.forEach((id, i) => {
                if (i < activePlan.length - 1) {
                    const key = `${id}→${activePlan[i+1]}`;
                    if (!edgeKeys.has(key)) {
                        visEdges.push({
                            id: `path_${i}`,
                            from: id,
                            to: activePlan[i + 1],
                            color: { color: '#a5b4fc', highlight: '#6366f1', opacity: 0.8 },
                            width: 2,
                            dashes: [8, 4],
                            arrows: { to: { enabled: true, scaleFactor: 0.8 } },
                            smooth: { type: 'cubicBezier', forceDirection: 'vertical', roundness: 0.4 },
                        });
                    }
                }
            });

            // --- Build justification banner HTML ---
            const masteredCount = justification?.mastered_count ?? 0;
            const upcomingCount = justification?.upcoming_count ?? 0;
            const reason = justification?.reason ?? '';
            const justificationBanner = activePlan.length > 0 ? `
                <div style="padding:10px 16px;background:#fafafa;border-bottom:1px solid #e2e8f0;font-size:12.5px;color:#475569;display:flex;gap:16px;flex-wrap:wrap;align-items:center;">
                    <span style="font-weight:600;color:#1e293b;">📋 Path Justification:</span>
                    <span>${reason}</span>
                    <span style="margin-left:auto;display:flex;gap:12px;">
                        <span style="color:#10b981;font-weight:600;">✅ ${masteredCount} mastered</span>
                        <span style="color:#f59e0b;font-weight:600;">🎯 1 current</span>
                        <span style="color:#6366f1;font-weight:600;">🔵 ${upcomingCount} upcoming</span>
                    </span>
                </div>` : '';

            roadmapMeta.textContent = `${activePlan.length > 0 ? `Learning Path: ${activePlan.length} steps · ` : ''}${allNodes.length} concepts · ${allEdges.length} prerequisites`;
            mermaidContainer.innerHTML = `
                ${justificationBanner}
                <div style="display:flex;gap:16px;padding:8px 16px;background:#ffffff;border-bottom:1px solid #e2e8f0;flex-wrap:wrap;align-items:center;">
                    <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;">
                        <div style="width:14px;height:14px;border-radius:3px;background:#d1fae5;border:2px solid #10b981;"></div> Mastered
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;">
                        <div style="width:14px;height:14px;border-radius:3px;background:#fef3c7;border:2px solid #f59e0b;"></div> Currently Learning
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;">
                        <div style="width:14px;height:14px;border-radius:3px;background:#ede9fe;border:2px solid #6366f1;"></div> Upcoming
                    </div>
                    <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;">
                        <div style="width:14px;height:14px;border-radius:3px;background:#f8fafc;border:1px solid #cbd5e1;"></div> Related Knowledge
                    </div>
                    <div style="margin-left:auto;font-size:11px;color:#94a3b8;">Drag · Scroll to zoom · Hover for details</div>
                </div>
                <div id="visGraphContainer" style="width:100%;height:calc(100% - ${activePlan.length > 0 ? 88 : 44}px);background-color:#f8fafc;"></div>
            `;

            // Render vis.js graph
            const container = document.getElementById('visGraphContainer');
            const network = new vis.Network(
                container,
                {
                    nodes: new vis.DataSet(visNodes),
                    edges: new vis.DataSet(visEdges)
                },
                {
                    layout: { improvedLayout: true },
                    physics: {
                        enabled: true,
                        solver: 'forceAtlas2Based',
                        forceAtlas2Based: {
                            gravitationalConstant: -60,
                            centralGravity: 0.003,
                            springLength: 140,
                            springConstant: 0.08,
                            damping: 0.5,
                        },
                        stabilization: { iterations: 400, updateInterval: 25 },
                    },
                    interaction: {
                        hover: true,
                        tooltipDelay: 150,
                        zoomView: true,
                        dragView: true,
                        navigationButtons: false,
                    },
                    nodes: { shape: 'box', borderWidthSelected: 3, chosen: true },
                    edges: { chosen: true, hoverWidth: 2 },
                }
            );

            // After stabilization, fit to view
            network.on('stabilizationIterationsDone', () => {
                network.setOptions({ physics: { enabled: false } });
                network.fit({ animation: { duration: 600, easingFunction: 'easeInOutQuad' } });
            });
        })
        .catch(() => {
            mermaidContainer.innerHTML = `<div style="text-align:center;padding:80px 20px;color:#ef4444;">Failed to load knowledge graph.</div>`;
        });
}

function hideRoadmap() {
    roadmapModal.classList.add('opacity-0', 'pointer-events-none');
    roadmapModal.firstElementChild.classList.add('scale-95');
}

showRoadmapBtn.addEventListener('click', showRoadmap);
closeRoadmapModal.addEventListener('click', hideRoadmap);
roadmapModal.addEventListener('click', e => { if (e.target === roadmapModal) hideRoadmap(); });

// ------------------------------------------------------------------ //
// Video Library
// ------------------------------------------------------------------ //
const videoLibraryModal   = document.getElementById('videoLibraryModal');
const closeVideoLibraryModal = document.getElementById('closeVideoLibraryModal');
const videoLibraryContent = document.getElementById('videoLibraryContent');
const videoLibraryMeta    = document.getElementById('videoLibraryMeta');
const videoSearchInput    = document.getElementById('videoSearchInput');
const showVideosBtn       = document.getElementById('showVideosBtn');

let _allVideoTopics = [];  // cache for filter/search

const STATUS_CONFIG = {
    mastered:  { label: '✅ Mastered',           badge: 'bg-emerald-50 text-emerald-700 border-emerald-200', bar: '#10b981' },
    current:   { label: '🎯 Currently Learning', badge: 'bg-amber-50  text-amber-700  border-amber-200',  bar: '#f59e0b' },
    upcoming:  { label: '🔵 Upcoming',           badge: 'bg-indigo-50 text-indigo-700 border-indigo-200', bar: '#4f46e5' },
};

function renderVideoTopics(topics) {
    if (!topics.length) {
        videoLibraryContent.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full text-slate-500 gap-3">
                <i class="fa-brands fa-youtube text-4xl text-red-600/60"></i>
                <p class="text-sm">No topics match your filter.</p>
            </div>`;
        return;
    }

    videoLibraryContent.innerHTML = topics.map(t => {
        const sc = STATUS_CONFIG[t.status] || STATUS_CONFIG.upcoming;
        const videoLinks = t.videos.map(v => `
            <a href="${v.url}" target="_blank" rel="noopener"
                class="flex items-center gap-2 px-3 py-2 rounded-lg bg-card hover:bg-surface border border-border hover:border-indigo-300 transition-all group text-xs text-slate-600 hover:text-slate-900">
                <i class="fa-brands fa-youtube text-red-500 text-base flex-shrink-0 group-hover:scale-110 transition-transform"></i>
                <span class="truncate">${v.label}</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[9px] ml-auto opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"></i>
            </a>`).join('');

        return `
        <div class="video-topic-card mb-4 bg-surface/60 border border-border rounded-xl overflow-hidden" data-status="${t.status}" data-name="${t.name.toLowerCase()}">
            <!-- Mastery progress bar (top accent) -->
            <div class="h-1 w-full" style="background:linear-gradient(to right, ${sc.bar} ${t.mastery_pct}%, #1e1e2e ${t.mastery_pct}%);"></div>
            
            <div class="p-4">
                <!-- Topic Header -->
                <div class="flex items-start justify-between gap-3 mb-3">
                    <div class="flex items-center gap-2 min-w-0">
                        <span class="flex-shrink-0 w-6 h-6 rounded-md bg-card border border-border text-[10px] font-bold text-slate-500 flex items-center justify-center">${t.step}</span>
                        <h3 class="font-semibold text-sm text-slate-800 truncate">${t.name}</h3>
                    </div>
                    <div class="flex items-center gap-2 flex-shrink-0">
                        <span class="text-[10px] px-2 py-0.5 rounded-full border ${sc.badge}">${sc.label}</span>
                        <span class="text-[10px] text-gray-500">${t.mastery_pct}%</span>
                    </div>
                </div>
                ${t.desc ? `<p class="text-[11px] text-gray-500 mb-3 line-clamp-2">${t.desc}</p>` : ''}
                <!-- Video Links -->
                <div class="space-y-1.5">
                    ${videoLinks}
                </div>
            </div>
        </div>`;
    }).join('');
}

function applyVideoFilters() {
    const searchTerm = videoSearchInput.value.toLowerCase().trim();
    const activeFilter = document.querySelector('.video-filter-btn.active')?.dataset.filter || 'all';

    const filtered = _allVideoTopics.filter(t => {
        const matchSearch = !searchTerm || t.name.toLowerCase().includes(searchTerm);
        const matchFilter = activeFilter === 'all' || t.status === activeFilter;
        return matchSearch && matchFilter;
    });

    renderVideoTopics(filtered);
}

function showVideoLibrary() {
    videoLibraryModal.classList.remove('opacity-0', 'pointer-events-none');
    videoLibraryModal.firstElementChild.classList.remove('scale-95');

    if (!state.studentId || !state.sessionId) {
        videoLibraryContent.innerHTML = `<div class="flex flex-col items-center justify-center h-full text-gray-500 gap-2">
            <i class="fa-solid fa-triangle-exclamation text-2xl text-amber-600"></i>
            <p class="text-sm">Please start a learning session first.</p>
        </div>`;
        return;
    }

    // Show spinner while loading
    videoLibraryContent.innerHTML = `<div class="flex items-center justify-center h-full">
        <i class="fa-solid fa-circle-notch fa-spin text-3xl text-red-400"></i>
    </div>`;
    videoLibraryMeta.textContent = 'Loading…';

    fetch(`/api/videos?student_id=${encodeURIComponent(state.studentId)}&session_id=${encodeURIComponent(state.sessionId)}`)
        .then(r => r.json())
        .then(data => {
            _allVideoTopics = data.topics || [];
            const mastered  = _allVideoTopics.filter(t => t.status === 'mastered').length;
            const current   = _allVideoTopics.filter(t => t.status === 'current').length;
            const upcoming  = _allVideoTopics.filter(t => t.status === 'upcoming').length;
            videoLibraryMeta.textContent = `${_allVideoTopics.length} topics · ✅ ${mastered} mastered · 🎯 ${current} current · 🔵 ${upcoming} upcoming`;

            // Reset filters
            videoSearchInput.value = '';
            document.querySelectorAll('.video-filter-btn').forEach(b => b.classList.remove('active'));
            document.querySelector('.video-filter-btn[data-filter="all"]').classList.add('active');

            renderVideoTopics(_allVideoTopics);
        })
        .catch(() => {
            videoLibraryContent.innerHTML = `<div class="text-center text-red-400 py-12">Failed to load video library.</div>`;
        });
}

function hideVideoLibrary() {
    videoLibraryModal.classList.add('opacity-0', 'pointer-events-none');
    videoLibraryModal.firstElementChild.classList.add('scale-95');
}

// Filter button clicks
document.querySelectorAll('.video-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.video-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        applyVideoFilters();
    });
});

// Live search
videoSearchInput.addEventListener('input', applyVideoFilters);

// Open / close
showVideosBtn.addEventListener('click', showVideoLibrary);
closeVideoLibraryModal.addEventListener('click', hideVideoLibrary);
videoLibraryModal.addEventListener('click', e => { if (e.target === videoLibraryModal) hideVideoLibrary(); });


// ================================================================== //
// Teacher Console Functionality
// ================================================================== //

// DOM References for Teacher Portal
const tabStudent          = document.getElementById('tabStudent');
const tabTeacher          = document.getElementById('tabTeacher');
const teacherLoginForm    = document.getElementById('teacherLoginForm');
const onboardTeacherId    = document.getElementById('onboardTeacherId');
const teacherStartBtn     = document.getElementById('teacherStartBtn');

const teacherShell        = document.getElementById('teacherShell');
const teacherHeaderId     = document.getElementById('teacherHeaderId');
const teacherLogoutBtn    = document.getElementById('teacherLogoutBtn');
const addStudentForm      = document.getElementById('addStudentForm');
const addStudentIdInput   = document.getElementById('addStudentIdInput');
const teacherStudentList  = document.getElementById('teacherStudentList');

const teacherPlaceholder        = document.getElementById('teacherPlaceholder');
const teacherStudentDashboard  = document.getElementById('teacherStudentDashboard');
const teacherSelectedStudentTitle = document.getElementById('teacherSelectedStudentTitle');

const statTotalSessions   = document.getElementById('statTotalSessions');
const statTotalDoubts     = document.getElementById('statTotalDoubts');
const statMasteryRate     = document.getElementById('statMasteryRate');

const dashboardStrongTopics     = document.getElementById('dashboardStrongTopics');
const dashboardWeakTopics       = document.getElementById('dashboardWeakTopics');
const dashboardUnstartedTopics  = document.getElementById('dashboardUnstartedTopics');
const dashboardActivePaths      = document.getElementById('dashboardActivePaths');
const dashboardDoubtLog         = document.getElementById('dashboardDoubtLog');
const dashboardActivityFeed     = document.getElementById('dashboardActivityFeed');

// Login Tabs Switchers
tabStudent.addEventListener('click', () => {
    tabStudent.className = "flex-1 pb-3 text-center border-b-2 border-primary text-sm font-semibold text-primary transition-all";
    tabTeacher.className = "flex-1 pb-3 text-center border-b-2 border-transparent text-sm font-semibold text-slate-500 hover:text-slate-800 transition-all";
    onboardingForm.classList.remove('hidden');
    teacherLoginForm.classList.add('hidden');
});

tabTeacher.addEventListener('click', () => {
    tabTeacher.className = "flex-1 pb-3 text-center border-b-2 border-primary text-sm font-semibold text-primary transition-all";
    tabStudent.className = "flex-1 pb-3 text-center border-b-2 border-transparent text-sm font-semibold text-slate-500 hover:text-slate-800 transition-all";
    teacherLoginForm.classList.remove('hidden');
    onboardingForm.classList.add('hidden');
});

// Teacher Login Action
teacherLoginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const teacherId = onboardTeacherId.value.trim();
    if (!teacherId) return;

    teacherStartBtn.disabled = true;
    teacherStartBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Entering Console…';

    try {
        state.teacherId = teacherId;
        teacherHeaderId.textContent = teacherId;
        
        onboardingOverlay.classList.add('fade-out');
        setTimeout(() => {
            onboardingOverlay.classList.add('hidden');
            teacherShell.classList.remove('hidden');
            teacherShell.classList.add('flex');
        }, 380);

        await loadMonitoredStudents();
        
        state.selectedStudentId = '';
        teacherPlaceholder.classList.remove('hidden');
        teacherStudentDashboard.classList.add('hidden');
    } catch (err) {
        console.error(err);
        alert('Failed to load teacher console. Is the backend running?');
    } finally {
        teacherStartBtn.disabled = false;
        teacherStartBtn.innerHTML = '<i class="fa-solid fa-right-to-bracket"></i> Enter Teacher Console';
    }
});

// Load Monitored Students
async function loadMonitoredStudents() {
    if (!state.teacherId) return;
    try {
        const res = await fetch(`/api/teacher/${encodeURIComponent(state.teacherId)}/students`);
        const data = await res.json();
        state.monitoredStudents = data.students || [];
        renderMonitoredStudentsList();
    } catch (err) {
        console.warn('Failed to load monitored students', err);
    }
}

// Render Monitored Students List
function renderMonitoredStudentsList() {
    if (!state.monitoredStudents.length) {
        teacherStudentList.innerHTML = `
            <div class="text-center text-gray-600 text-xs py-8">
                <i class="fa-solid fa-users-slash text-2xl mb-2 block"></i>
                No students monitored yet
            </div>`;
        return;
    }

    teacherStudentList.innerHTML = state.monitoredStudents.map(studentId => `
        <div class="student-item group ${studentId === state.selectedStudentId ? 'active' : ''}"
             data-id="${studentId}" onclick="selectStudent('${studentId}')">
            <div class="flex items-center gap-2 min-w-0 flex-1">
                <i class="fa-solid fa-user-graduate text-indigo-500 text-xs flex-shrink-0"></i>
                <span class="truncate font-semibold text-xs text-slate-700 group-hover:text-slate-900">${studentId}</span>
            </div>
            <button onclick="event.stopPropagation(); removeMonitoredStudent('${studentId}')" 
                class="opacity-0 group-hover:opacity-100 hover:opacity-100 text-red-500 hover:text-red-600 p-1 rounded transition-all hover:bg-red-50" 
                title="Remove student">
                <i class="fa-solid fa-trash-can text-[10px]"></i>
            </button>
        </div>
    `).join('');
}

// Add Monitored Student
addStudentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const studentId = addStudentIdInput.value.trim();
    if (!studentId || !state.teacherId) return;

    try {
        const res = await fetch(`/api/teacher/${encodeURIComponent(state.teacherId)}/students`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: studentId })
        });
        if (!res.ok) throw new Error('Failed to add student');
        
        addStudentIdInput.value = '';
        await loadMonitoredStudents();
        selectStudent(studentId);
    } catch (err) {
        alert('Failed to add student.');
    }
});

// Remove Monitored Student
async function removeMonitoredStudent(studentId) {
    if (!confirm(`Are you sure you want to remove student "${studentId}" from your monitored list?`)) return;
    try {
        const res = await fetch(`/api/teacher/${encodeURIComponent(state.teacherId)}/students/${encodeURIComponent(studentId)}`, {
            method: 'DELETE'
        });
        if (!res.ok) throw new Error('Failed to remove student');
        
        if (state.selectedStudentId === studentId) {
            state.selectedStudentId = '';
            teacherPlaceholder.classList.remove('hidden');
            teacherStudentDashboard.classList.add('hidden');
        }
        await loadMonitoredStudents();
    } catch (err) {
        alert('Failed to remove student.');
    }
}

// Select Student and Load Progress
async function selectStudent(studentId) {
    state.selectedStudentId = studentId;
    
    document.querySelectorAll('.student-item').forEach(el => {
        el.classList.toggle('active', el.dataset.id === studentId);
    });

    teacherPlaceholder.classList.add('hidden');
    teacherStudentDashboard.classList.remove('hidden');
    
    teacherSelectedStudentTitle.textContent = studentId;
    
    const spinner = `<div class="flex justify-center py-8"><i class="fa-solid fa-circle-notch fa-spin text-xl text-indigo-500"></i></div>`;
    dashboardStrongTopics.innerHTML = spinner;
    dashboardWeakTopics.innerHTML = spinner;
    dashboardUnstartedTopics.innerHTML = spinner;
    dashboardActivePaths.innerHTML = spinner;
    dashboardDoubtLog.innerHTML = spinner;
    dashboardActivityFeed.innerHTML = spinner;

    statTotalSessions.textContent = '-';
    statTotalDoubts.textContent = '-';
    statMasteryRate.textContent = '-%';

    try {
        const res = await fetch(`/api/teacher/student/${encodeURIComponent(studentId)}/progress`);
        if (!res.ok) throw new Error('Failed to fetch student progress');
        const data = await res.json();
        
        renderStudentProgress(data);
    } catch (err) {
        console.error(err);
        const errMsg = `<div class="text-xs text-red-400 py-4">Error loading progress data.</div>`;
        dashboardStrongTopics.innerHTML = errMsg;
        dashboardWeakTopics.innerHTML = errMsg;
        dashboardUnstartedTopics.innerHTML = errMsg;
        dashboardActivePaths.innerHTML = errMsg;
        dashboardDoubtLog.innerHTML = errMsg;
        dashboardActivityFeed.innerHTML = errMsg;
    }
}

// Render Student Progress Report
function renderStudentProgress(data) {
    const sessions = data.sessions || [];
    const doubts = data.doubts || [];
    const mp = data.mastery_profile || {};
    
    const strong = mp.strong_topics || [];
    const weak = mp.weak_topics || [];
    const unstarted = mp.unstarted_topics || [];
    
    const totalConcepts = strong.length + weak.length + unstarted.length;
    const masteryRate = totalConcepts > 0 ? Math.round((strong.length / totalConcepts) * 100) : 0;
    
    statTotalSessions.textContent = sessions.length;
    statTotalDoubts.textContent = doubts.length;
    statMasteryRate.textContent = `${masteryRate}%`;
    
    // Strong Topics
    if (strong.length === 0) {
        dashboardStrongTopics.innerHTML = `<div class="text-xs text-slate-500 italic py-2">No concepts mastered yet (&ge; 80% score).</div>`;
    } else {
        dashboardStrongTopics.innerHTML = strong.map(c => `
            <div class="bg-surface/50 border border-border/60 rounded-xl p-3">
                <div class="flex items-center justify-between mb-1.5">
                    <span class="text-xs font-semibold text-slate-800">${c.name}</span>
                    <span class="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded-full font-semibold">${c.mastery_pct}%</span>
                </div>
                <div class="h-1.5 w-full bg-surface rounded-full overflow-hidden">
                    <div class="h-full bg-emerald-500 rounded-full" style="width: ${c.mastery_pct}%;"></div>
                </div>
                ${c.desc ? `<p class="text-[10px] text-slate-500 mt-1 line-clamp-1">${escapeHtml(c.desc)}</p>` : ''}
            </div>
        `).join('');
    }
    
    // Weak Topics
    if (weak.length === 0) {
        dashboardWeakTopics.innerHTML = `<div class="text-xs text-slate-500 italic py-2">No active learning topics in progress (0% &lt; score &lt; 80%).</div>`;
    } else {
        dashboardWeakTopics.innerHTML = weak.map(c => `
            <div class="bg-surface/50 border border-border/60 rounded-xl p-3">
                <div class="flex items-center justify-between mb-1.5">
                    <span class="text-xs font-semibold text-slate-800">${c.name}</span>
                    <span class="text-[10px] text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded-full font-semibold">${c.mastery_pct}%</span>
                </div>
                <div class="h-1.5 w-full bg-surface rounded-full overflow-hidden">
                    <div class="h-full bg-amber-500 rounded-full" style="width: ${c.mastery_pct}%;"></div>
                </div>
                ${c.desc ? `<p class="text-[10px] text-slate-500 mt-1 line-clamp-1">${escapeHtml(c.desc)}</p>` : ''}
            </div>
        `).join('');
    }
    
    // Unstarted
    if (unstarted.length === 0) {
        dashboardUnstartedTopics.innerHTML = `<div class="text-xs text-slate-500 italic py-1">No other concepts in database.</div>`;
    } else {
        dashboardUnstartedTopics.innerHTML = `
            <div class="flex flex-wrap gap-1.5">
                ${unstarted.map(c => `
                    <span class="text-[10px] px-2 py-1 bg-surface/50 border border-border rounded-lg text-slate-600 font-semibold" title="${escapeHtml(c.desc || '')}">
                        ${c.name}
                    </span>
                `).join('')}
            </div>`;
    }
    
    // Active Paths
    if (sessions.length === 0) {
        dashboardActivePaths.innerHTML = `<div class="text-xs text-slate-500 italic py-2">No learning sessions found for this student.</div>`;
    } else {
        dashboardActivePaths.innerHTML = sessions.map(s => {
            const planNames = s.active_plan_names || [];
            const planSeqHtml = planNames.length > 0 
                ? `<div class="mt-2 flex flex-wrap items-center gap-1.5">
                     ${planNames.map((name, i) => `
                        <span class="text-[10px] px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold">${name}</span>
                        ${i < planNames.length - 1 ? '<i class="fa-solid fa-arrow-right text-slate-400 text-[8px]"></i>' : ''}
                     `).join('')}
                   </div>`
                : `<span class="text-[10px] text-slate-500 block mt-1">Default/No customized path computed yet</span>`;
                
            return `
                <div class="bg-surface/50 border border-border/60 rounded-xl p-3.5">
                    <div class="flex items-center justify-between gap-2">
                        <span class="text-xs font-semibold text-slate-800">${escapeHtml(s.topic || 'Untitled Session')}</span>
                        <span class="text-[9px] text-slate-500">${timeAgo(s.updated_at || s.created_at)}</span>
                    </div>
                    <div class="text-[10px] text-slate-500 mt-1 flex items-center gap-2">
                        <span>${s.turn_count || 0} discussion turns</span>
                        <span>·</span>
                        <span>Session ID: ${s.session_id.substring(0, 8)}...</span>
                    </div>
                    ${planSeqHtml}
                </div>
            `;
        }).join('');
    }
    
    // Doubt Log
    if (doubts.length === 0) {
        dashboardDoubtLog.innerHTML = `<div class="text-xs text-slate-500 italic py-2">No misconceptions or doubts recorded. The student is learning smoothly!</div>`;
    } else {
        dashboardDoubtLog.innerHTML = doubts.map(d => `
            <div class="bg-red-50 border border-red-200 rounded-xl p-3.5 space-y-2">
                <div class="flex items-center justify-between gap-2 border-b border-red-100 pb-1.5">
                    <span class="text-[10px] text-red-700 font-semibold uppercase tracking-wider"><i class="fa-solid fa-triangle-exclamation mr-1"></i>Misconception Detected</span>
                    <span class="text-[9px] text-slate-500">${timeAgo(d.timestamp)}</span>
                </div>
                <div>
                    <span class="block text-[10px] font-bold text-slate-500 uppercase tracking-widest">Student Question</span>
                    <p class="text-xs text-slate-700 italic mt-0.5">&ldquo;${escapeHtml(d.user_input)}&rdquo;</p>
                </div>
                <div>
                    <span class="block text-[10px] font-bold text-slate-500 uppercase tracking-widest">Tutor Guidance / Explanation</span>
                    <div class="text-xs text-slate-700 mt-1 chat-bubble max-w-none bg-white border border-border p-2.5 rounded-xl leading-relaxed">
                        ${marked.parse(d.final_response)}
                    </div>
                </div>
                ${d.affected_concepts && d.affected_concepts.length > 0 ? `
                    <div class="flex flex-wrap items-center gap-1.5 mt-1.5">
                        <span class="text-[9px] text-slate-500 uppercase tracking-wider">Affected:</span>
                        ${d.affected_concepts.map(c => `<span class="text-[9px] px-1.5 py-0.5 bg-red-50 border border-red-200 text-red-700 rounded font-semibold">${c}</span>`).join('')}
                    </div>` : ''}
            </div>
        `).join('');
    }
    
    // Activity Feed
    const feed = data.recent_activity || [];
    if (feed.length === 0) {
        dashboardActivityFeed.innerHTML = `<div class="text-xs text-slate-500 italic py-2">No chat exchanges recorded yet.</div>`;
    } else {
        dashboardActivityFeed.innerHTML = feed.map(turn => `
            <div class="border-l-2 border-border pl-4 space-y-1.5 py-1">
                <div class="flex items-center justify-between text-[9px] text-slate-500">
                    <span>${turn.session_id ? `Session ID: ${turn.session_id.substring(0, 8)}...` : ''}</span>
                    <span>${timeAgo(turn.timestamp)}</span>
                </div>
                <div class="flex items-start gap-1.5">
                    <span class="text-[10px] font-semibold text-indigo-600 uppercase tracking-wider mt-0.5 flex-shrink-0 w-8">User:</span>
                    <p class="text-xs text-slate-700 font-medium">&ldquo;${escapeHtml(turn.user_input)}&rdquo;</p>
                </div>
                <div class="flex items-start gap-1.5">
                    <span class="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider mt-0.5 flex-shrink-0 w-8">Tutor:</span>
                    <div class="text-xs text-slate-700 chat-bubble max-w-none p-0 bg-transparent border-none leading-relaxed">
                        ${marked.parse(turn.final_response)}
                    </div>
                </div>
            </div>
        `).join('');
    }
}

// Teacher Logout Action
teacherLogoutBtn.addEventListener('click', () => {
    state.teacherId = '';
    state.selectedStudentId = '';
    
    teacherShell.classList.add('hidden');
    teacherShell.classList.remove('flex');
    onboardingOverlay.classList.remove('hidden');
    onboardingOverlay.classList.remove('fade-out');
    
    onboardTeacherId.value = 'teacher_123';
});

