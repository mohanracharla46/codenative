/**
 * CodeNative AI Chatbot Widget
 * Floating animated chatbot powered by Gemini 2.0 Flash
 * Self-contained – just include this script and it auto-injects the UI
 */

(function () {
    // ── Detect current language from the URL path ──────────────────────
    const pathLang = window.location.pathname.split('/')[1]?.replace('.html', '') || 'programming';
    const LANG = ['python', 'java', 'c'].includes(pathLang) ? pathLang : 'programming';

    const LANG_META = {
        python: { label: 'Python', color: '#3776ab', icon: 'fab fa-python', glow: 'rgba(55,118,171,0.45)' },
        java: { label: 'Java', color: '#ed8b00', icon: 'fab fa-java', glow: 'rgba(237,139,0,0.45)' },
        c: { label: 'C Language', color: '#00599c', icon: 'fas fa-code-branch', glow: 'rgba(0,89,156,0.45)' },
        programming: { label: 'Programming', color: '#6366f1', icon: 'fas fa-robot', glow: 'rgba(99,102,241,0.45)' }
    };
    const meta = LANG_META[LANG];

    // ── Inject global CSS ─────────────────────────────────────────────
    const style = document.createElement('style');
    style.textContent = `
        @keyframes cn-pulse  { 0%,100%{transform:scale(1);box-shadow:0 0 0 0 ${meta.glow};} 50%{transform:scale(1.08);box-shadow:0 0 0 14px rgba(0,0,0,0);} }
        @keyframes cn-bounce { 0%,100%{transform:translateY(0)} 40%{transform:translateY(-9px)} 70%{transform:translateY(-4px)} }
        @keyframes cn-slideUp{ from{opacity:0;transform:translateY(30px) scale(.95)} to{opacity:1;transform:translateY(0) scale(1)} }
        @keyframes cn-fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
        @keyframes cn-typing { 0%,80%,100%{opacity:.25} 40%{opacity:1} }
        @keyframes cn-shake  { 0%,100%{transform:translateX(0)} 20%,60%{transform:translateX(-5px)} 40%,80%{transform:translateX(5px)} }
        @keyframes cn-glow   { 0%,100%{box-shadow:0 0 12px ${meta.glow}} 50%{box-shadow:0 0 28px ${meta.glow}} }

        #cn-chat-fab {
            position:fixed; bottom:28px; right:28px; z-index:9999;
            width:60px; height:60px; border-radius:50%; border:none; cursor:pointer;
            background:${meta.color}; color:#fff; font-size:24px;
            display:flex; align-items:center; justify-content:center;
            animation:cn-pulse 2.8s ease-in-out infinite;
            transition:all .3s cubic-bezier(.175,.885,.32,1.275);
            box-shadow:0 8px 24px ${meta.glow};
        }
        #cn-chat-fab:hover{ transform:scale(1.15) rotate(-8deg)!important; }
        #cn-chat-fab .cn-badge{
            position:absolute; top:-3px; right:-3px; background:#ef4444;
            color:#fff; width:20px; height:20px; border-radius:50%;
            font-size:11px; font-weight:800; display:flex; align-items:center; justify-content:center;
            border:2px solid #fff; animation:cn-bounce 2s infinite;
        }

        #cn-chat-hint {
            position:fixed; bottom:98px; right:28px; z-index:9999;
            background:#fff; color:#1e293b; padding:5px 10px; border-radius:10px;
            font-size:10.5px; font-weight:800; font-family:'Inter',sans-serif;
            box-shadow:0 4px 15px rgba(0,0,0,0.1);
            animation:cn-bounce 3s infinite;
            pointer-events:none; border:1px solid rgba(0,0,0,0.05);
            transition:all .3s ease;
        }
        #cn-chat-hint.cn-hidden { opacity:0; transform:translateY(10px); }
        #cn-chat-hint::after {
            content:''; position:absolute; bottom:-6px; right:22px;
            border-left:6px solid transparent; border-right:6px solid transparent;
            border-top:6px solid #fff;
        }

        #cn-chat-window {
            position:fixed; bottom:100px; right:28px; z-index:9998;
            width:380px; max-height:560px;
            background:#fff; border-radius:24px;
            box-shadow:0 25px 60px rgba(0,0,0,.18), 0 0 0 1px rgba(0,0,0,.05);
            display:flex; flex-direction:column; overflow:hidden;
            animation:cn-slideUp .38s cubic-bezier(.175,.885,.32,1.275);
            transition:all .3s ease;
        }
        #cn-chat-window.cn-hidden{
            opacity:0; pointer-events:none; transform:translateY(30px) scale(.95);
        }

        .cn-header{
            background:${meta.color}; padding:16px 20px;
            display:flex; align-items:center; gap:12px; flex-shrink:0;
            position:relative; overflow:hidden;
        }
        .cn-header::before{
            content:''; position:absolute; inset:0;
            background:linear-gradient(135deg,rgba(255,255,255,.15) 0%,transparent 60%);
            pointer-events:none;
        }
        .cn-header-icon{
            width:42px; height:42px; border-radius:14px;
            background:rgba(255,255,255,.22); display:flex; align-items:center; justify-content:center;
            font-size:20px; color:#fff; flex-shrink:0; animation:cn-glow 3s ease-in-out infinite;
        }
        .cn-header-text h3{ margin:0; font-size:15px; font-weight:800; color:#fff; font-family:'Inter',sans-serif; }
        .cn-header-text p { margin:0; font-size:11px; color:rgba(255,255,255,.8); font-family:'Inter',sans-serif; }
        .cn-close-btn{
            margin-left:auto; background:rgba(255,255,255,.2); border:none; color:#fff;
            width:32px; height:32px; border-radius:10px; cursor:pointer; font-size:16px;
            display:flex; align-items:center; justify-content:center; transition:.2s;
            flex-shrink:0;
        }
        .cn-close-btn:hover{ background:rgba(255,255,255,.35); transform:scale(1.1); }

        #cn-messages{
            flex:1; overflow-y:auto; padding:20px 16px 10px; display:flex;
            flex-direction:column; gap:12px; min-height:0;
            scroll-behavior:smooth;
        }
        #cn-messages::-webkit-scrollbar{ width:4px; }
        #cn-messages::-webkit-scrollbar-thumb{ background:#e2e8f0; border-radius:4px; }

        .cn-msg{ display:flex; gap:8px; animation:cn-fadeIn .3s ease; max-width:90%; }
        .cn-msg.cn-user{ align-self:flex-end; flex-direction:row-reverse; }
        .cn-msg.cn-bot { align-self:flex-start; }

        .cn-avatar{
            width:30px; height:30px; border-radius:10px;
            display:flex; align-items:center; justify-content:center;
            font-size:13px; flex-shrink:0; margin-top:2px;
        }
        .cn-bot  .cn-avatar{ background:${meta.color}; color:#fff; }
        .cn-user .cn-avatar{ background:#f1f5f9; color:#64748b; }

        .cn-bubble{
            padding:10px 14px; border-radius:16px; font-size:13.5px; line-height:1.6;
            font-family:'Inter',sans-serif; max-width:100%; word-break:break-word;
        }
        .cn-bot  .cn-bubble{ background:#f8fafc; color:#1e293b; border:1px solid #f1f5f9; border-bottom-left-radius:4px; }
        .cn-user .cn-bubble{ background:${meta.color}; color:#fff; border-bottom-right-radius:4px; }
        .cn-bubble pre{ background:#0f172a; color:#f8fafc; padding:10px 12px; border-radius:8px; font-size:12px; overflow-x:auto; margin:8px 0 0; }
        .cn-bubble code{ font-family:'JetBrains Mono',Consolas,monospace; }

        .cn-typing-indicator{ display:flex; align-items:center; gap:5px; padding:4px 8px; }
        .cn-typing-indicator span{
            width:7px; height:7px; background:${meta.color}; border-radius:50%;
            animation:cn-typing 1.4s ease-in-out infinite;
        }
        .cn-typing-indicator span:nth-child(2){ animation-delay:.2s; }
        .cn-typing-indicator span:nth-child(3){ animation-delay:.4s; }

        .cn-input-area{
            padding:12px 16px 16px; border-top:1px solid #f1f5f9;
            display:flex; gap:8px; align-items:flex-end; flex-shrink:0;
            background:#fff;
        }
        #cn-input{
            flex:1; border:1.5px solid #e2e8f0; border-radius:14px;
            padding:10px 14px; font-size:13.5px; font-family:'Inter',sans-serif;
            resize:none; outline:none; max-height:100px; overflow-y:auto;
            transition:.2s; color:#1e293b; line-height:1.5;
        }
        #cn-input:focus{ border-color:${meta.color}; box-shadow:0 0 0 3px ${meta.glow.replace('.45', '.15')}; }
        #cn-input::placeholder{ color:#94a3b8; }

        #cn-send{
            width:42px; height:42px; border-radius:12px; border:none; cursor:pointer;
            background:${meta.color}; color:#fff; font-size:16px;
            display:flex; align-items:center; justify-content:center;
            transition:.2s; flex-shrink:0;
        }
        #cn-send:hover:not(:disabled){ transform:translateY(-2px) scale(1.05); box-shadow:0 6px 16px ${meta.glow}; }
        #cn-send:disabled{ opacity:.5; cursor:not-allowed; transform:none!important; }

        .cn-welcome-chip{
            background:#f8fafc; border:1px solid #f1f5f9; border-radius:20px;
            padding:6px 14px; font-size:12px; font-weight:600; color:#64748b;
            cursor:pointer; transition:.2s; white-space:nowrap; font-family:'Inter',sans-serif;
        }
        .cn-welcome-chip:hover{ background:${meta.color}; color:#fff; border-color:${meta.color}; transform:translateY(-2px); }
        .cn-chips{ display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }

        @media(max-width:480px){
            #cn-chat-window{ width:calc(100vw - 24px); right:12px; bottom:84px; }
            #cn-chat-fab{ bottom:16px; right:16px; }
        }
    `;
    document.head.appendChild(style);

    // ── Quick question chips per language ─────────────────────────────
    const CHIPS = {
        python: ['Function ante enti ra?', 'Loop ela use cheyali?', 'Error fix cheyyi 🔥'],
        java: ['Class ante enti ra?', 'Exception handle ela?', 'Code error fix cheyyi'],
        c: ['Pointer ante enti ra?', 'malloc() ela use cheyali?', 'Error fix cheyyi'],
        programming: ['Coding ela start cheyali?', 'Variable ante enti?', 'Error vastundi help!']
    };

    // ── Build HTML ────────────────────────────────────────────────────
    document.body.insertAdjacentHTML('beforeend', `
    <div id="cn-chat-hint">Ask in telugu</div>
    <button id="cn-chat-fab" title="Ask AI Doubt">
        <i class="${meta.icon}"></i>
        <span class="cn-badge">AI</span>
    </button>

    <div id="cn-chat-window" class="cn-hidden">
        <div class="cn-header">
            <div class="cn-header-icon"><i class="${meta.icon}"></i></div>
            <div class="cn-header-text">
                <h3>CodeNative AI 🤖</h3>
                <p>${meta.label} Coding Friend · Ela unnav? 😄</p>
            </div>
            <button class="cn-close-btn" id="cn-close"><i class="fas fa-times"></i></button>
        </div>

        <div id="cn-messages">
            <div class="cn-msg cn-bot">
                <div class="cn-avatar"><i class="${meta.icon}"></i></div>
                <div>
                    <div class="cn-bubble">
                        Hey ra! 👋 Nenu nee <strong>${meta.label} coding friend</strong> — CodeNative AI 😄<br><br>
                        ${meta.label} lo doubt unte adugu ra, kalisi solve cheddaam 💻🔥
                        <div class="cn-chips">
                            ${(CHIPS[LANG] || CHIPS.programming).map(q => `<span class="cn-welcome-chip">${q}</span>`).join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="cn-input-area">
            <textarea id="cn-input" rows="1" placeholder="Coding doubt adugu ra... 👋"></textarea>
            <button id="cn-send"><i class="fas fa-paper-plane"></i></button>
        </div>
    </div>
    `);

    // ── References ────────────────────────────────────────────────────
    const fab = document.getElementById('cn-chat-fab');
    const hint = document.getElementById('cn-chat-hint');
    const window_ = document.getElementById('cn-chat-window');
    const closeBtn = document.getElementById('cn-close');
    const input = document.getElementById('cn-input');
    const sendBtn = document.getElementById('cn-send');
    const messages = document.getElementById('cn-messages');

    let isOpen = false;

    function toggleChat() {
        isOpen = !isOpen;
        window_.classList.toggle('cn-hidden', !isOpen);
        hint.classList.toggle('cn-hidden', isOpen);
        if (isOpen) { input.focus(); scrollToBottom(); }
    }

    fab.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);

    // Chip click handling
    messages.addEventListener('click', e => {
        if (e.target.classList.contains('cn-welcome-chip')) {
            input.value = e.target.textContent;
            sendMessage();
        }
    });

    // Auto-grow textarea
    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    });

    // Enter to send (Shift+Enter = newline)
    input.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
    sendBtn.addEventListener('click', sendMessage);

    function scrollToBottom() {
        setTimeout(() => { messages.scrollTop = messages.scrollHeight; }, 50);
    }

    function addMessage(role, html) {
        const isUser = role === 'user';
        const avatarIcon = isUser ? 'fas fa-user' : meta.icon;
        const div = document.createElement('div');
        div.className = `cn-msg cn-${role}`;
        div.innerHTML = `
            <div class="cn-avatar"><i class="${avatarIcon}"></i></div>
            <div class="cn-bubble">${html}</div>
        `;
        messages.appendChild(div);
        scrollToBottom();
        return div;
    }

    function addTypingIndicator() {
        const div = document.createElement('div');
        div.className = 'cn-msg cn-bot';
        div.id = 'cn-typing';
        div.innerHTML = `
            <div class="cn-avatar"><i class="${meta.icon}"></i></div>
            <div class="cn-bubble">
                <div class="cn-typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        messages.appendChild(div);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        document.getElementById('cn-typing')?.remove();
    }

    // Render markdown-ish code blocks: ```lang\ncode\n```
    function renderMarkdown(text) {
        // Escape HTML first
        let safe = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        // Code blocks ```...```
        safe = safe.replace(/```[\w]*\n?([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        // Inline code `...`
        safe = safe.replace(/`([^`]+)`/g, '<code style="background:#f1f5f9;padding:2px 5px;border-radius:4px;font-family:monospace;color:#6366f1;">$1</code>');
        // Bold **...**
        safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Links [text](url)
        safe = safe.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" style="color:#6366f1;font-weight:700;text-decoration:underline;">$1</a>');
        // Line breaks
        safe = safe.replace(/\n/g, '<br>');
        return safe;
    }

    async function sendMessage() {
        const text = input.value.trim();
        if (!text) {
            sendBtn.classList.add('cn-shake-anim');
            setTimeout(() => sendBtn.classList.remove('cn-shake-anim'), 500);
            return;
        }

        input.value = '';
        input.style.height = 'auto';
        sendBtn.disabled = true;

        addMessage('user', text);
        addTypingIndicator();

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, language: LANG })
            });
            
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.message || errorData.reply || `Server error: ${res.status}`);
            }
            
            const data = await res.json();
            removeTypingIndicator();
            addMessage('bot', renderMarkdown(data.reply || 'No response.'));
        } catch (err) {
            removeTypingIndicator();
            console.error('Chat error:', err);
            let errorMsg = '❌ Could not reach the AI. Please check your connection.';
            
            if (err.message.includes('401')) {
                // Use the message from server if possible, otherwise default
                errorMsg = err.message.length > 20 ? err.message : '⚠️ Please login to use the AI chatbot.';
            } else {
                if (err.message.includes('503')) errorMsg = '⚠️ AI Service is temporarily busy. Please try again in a moment.';
                if (err.message.includes('429')) errorMsg = '⏳ Daily limit reached. Please try again tomorrow!';
            }
            addMessage('bot', renderMarkdown(errorMsg));
        } finally {
            sendBtn.disabled = false;
            input.focus();
        }
    }
})();
