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
