// Initialize Ace Editor
const editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/python");
editor.setOptions({
    fontSize: "14px",
    showPrintMargin: false,
    tabSize: 4,
    useWorker: false
});

// DOM
const langSelect = document.getElementById("lang");
const runBtn = document.getElementById("runBtn");
const clearBtn = document.getElementById("clearBtn");
const outputEl = document.getElementById("output");

// Add notification styles dynamically
const style = document.createElement('style');
style.textContent = `
    .compiler-notice {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #1e293b;
        color: #fff;
        padding: 16px 24px;
        border-radius: 16px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.3);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        transform: translateY(-100px);
        opacity: 0;
        transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        max-width: 320px;
    }
    .compiler-notice.active {
        transform: translateY(0);
        opacity: 1;
    }
    .notice-icon {
        width: 40px;
        height: 40px;
        background: rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #818cf8;
        font-size: 18px;
        flex-shrink: 0;
    }
    .notice-content b { display: block; font-size: 14px; margin-bottom: 2px; }
    .notice-content p { margin: 0; font-size: 12px; color: #94a3b8; line-height: 1.4; }
`;
document.head.appendChild(style);

function showNotice() {
    let notice = document.getElementById('compiler-notice');
    if (!notice) {
        notice = document.createElement('div');
        notice.id = 'compiler-notice';
        notice.className = 'compiler-notice';
        notice.innerHTML = `
            <div class="notice-icon"><i class="fas fa-tools"></i></div>
            <div class="notice-content">
                <b>We are working on it!</b>
                <p>Please cooperate! 😊</p>        
            </div>
        `;
        document.body.appendChild(notice);
    }

    // Show it
    setTimeout(() => notice.classList.add('active'), 100);

    // Hide it after 4 seconds
    setTimeout(() => {
        notice.classList.remove('active');
    }, 4000);
}

// change mode and tab name on language select
langSelect.addEventListener("change", () => {
    const lang = langSelect.value;
    const tabFileName = document.querySelector(".file-name");

    if (lang == "71") {
        editor.session.setMode("ace/mode/python");
        tabFileName.innerText = "main.py";
    }
    else if (lang == "62") {
        editor.session.setMode("ace/mode/java");
        tabFileName.innerText = "Main.java";
    }
    else if (lang == "50") {
        editor.session.setMode("ace/mode/c_cpp");
        tabFileName.innerText = "main.c";
    }
    else if (lang == "54") {
        editor.session.setMode("ace/mode/c_cpp");
        tabFileName.innerText = "main.cpp";
    }
    else if (lang == "63") {
        editor.session.setMode("ace/mode/javascript");
        tabFileName.innerText = "script.js";
    }
});

// Run handler
runBtn.addEventListener("click", runCode);
clearBtn.addEventListener("click", () => {
    outputEl.innerText = "";
    console.log("Output cleared");
});

// runCode: sends code to /run and shows output
async function runCode() {
    showNotice();
    try {
        runBtn.disabled = true;
        runBtn.innerHTML = '<i class="fas fa-spinner fa-spin" style="font-size: 10px; margin-right: 6px;"></i> Running...';
        outputEl.innerText = "Running...";

        const code = editor.getValue();
        const language_id = langSelect.value;
        const stdin = document.getElementById("stdin") ? document.getElementById("stdin").value : "";

        const response = await fetch("/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code, language_id, stdin })
        });

        // If server returned non-JSON (rare), handle gracefully
        const text = await response.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch (err) {
            outputEl.innerText = `Invalid response from server:\n${text}`;
            return;
        }

        outputEl.innerText = data.output || "No output";
    } catch (err) {
        outputEl.innerText = `Error: ${err.message}`;
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = '<i class="fas fa-play" style="font-size: 10px; margin-right: 6px;"></i> Run Code';
    }
}
