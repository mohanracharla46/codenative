document.addEventListener('DOMContentLoaded', () => {
    // ── Active Study Session Logger ─────────────────────────────────────
    // Tracks study hours ONLY when the user is active on the website
    
    let lastActivityTime = Date.now();
    const ACTIVITY_THRESHOLD = 5 * 60 * 1000; // 5 minutes of idle time allowed

    // Update activity timestamp on user interaction
    const updateActivity = () => {
        lastActivityTime = Date.now();
    };

    ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart', 'click'].forEach(event => {
        window.addEventListener(event, updateActivity, { passive: true });
    });

    // Logger runs every 1 minute
    setInterval(async () => {
        try {
            const now = Date.now();
            const isTabVisible = document.visibilityState === 'visible';
            const isActive = (now - lastActivityTime) < ACTIVITY_THRESHOLD;

            // Only log if the tab is visible AND the user has interacted recently
            if (isTabVisible && isActive) {
                await fetch('/api/log_study', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
            }
        } catch (e) {
            // Silently fail if offline or not logged in
        }
    }, 60000); // 1 minute interval

    // ── Global Proactive Feedback Widget ────────────────────────────────
    const injectFeedbackWidget = () => {
        // Don't show on admin pages or if already submitted in this session
        if (window.location.pathname.startsWith('/admin') || sessionStorage.getItem('feedback_prompted')) return;

        const widgetHtml = `
            <div id="global-feedback-trigger" class="feedback-fab" title="Give Feedback">
                <i class="fas fa-comment-dots"></i>
            </div>
            <div id="feedback-modal" class="feedback-modal">
                <div class="feedback-modal-content">
                    <button id="close-feedback" class="close-btn">&times;</button>
                    <h2>How are we doing? 😊</h2>
                    <p>Your feedback helps us make Code Native better for everyone.</p>
                    <div class="stars" id="modal-stars">
                        <i class="fas fa-star" data-v="1"></i>
                        <i class="fas fa-star" data-v="2"></i>
                        <i class="fas fa-star" data-v="3"></i>
                        <i class="fas fa-star" data-v="4"></i>
                        <i class="fas fa-star" data-v="5"></i>
                    </div>
                    <input type="text" id="modal-college" placeholder="College Name" class="modal-input">
                    <textarea id="modal-message" placeholder="What can we improve?"></textarea>
                    <button id="submit-modal-feedback" class="submit-btn">Send Feedback</button>
                </div>
            </div>
            <style>
                .feedback-fab {
                    position: fixed; bottom: 30px; right: 30px;
                    width: 60px; height: 60px;
                    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
                    color: white; border-radius: 50%;
                    display: flex; align-items: center; justify-content: center;
                    font-size: 24px; cursor: pointer; z-index: 9999;
                    box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4);
                    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                }
                .feedback-fab:hover { transform: scale(1.1) rotate(5deg); }
                .feedback-modal {
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(8px);
                    display: none; align-items: center; justify-content: center; z-index: 10000;
                }
                .feedback-modal-content {
                    background: white; padding: 2.5rem; border-radius: 24px;
                    width: 90%; max-width: 400px; position: relative;
                    text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                }
                .feedback-modal-content h2 { margin-top: 0; color: #1e293b; }
                .feedback-modal-content p { color: #64748b; margin-bottom: 1.5rem; }
                .close-btn {
                    position: absolute; top: 15px; right: 20px;
                    background: none; border: none; font-size: 24px; cursor: pointer; color: #94a3b8;
                }
                .stars { font-size: 2rem; color: #e2e8f0; margin-bottom: 1.5rem; cursor: pointer; }
                .stars i.active { color: #f59e0b; }
                .modal-input {
                    width: 100%; padding: 0.8rem 1rem; border-radius: 12px; border: 2px solid #f1f5f9;
                    margin-bottom: 1rem; font-family: inherit; font-size: 0.9rem;
                }
                #modal-message {
                    width: 100%; padding: 1rem; border-radius: 12px; border: 2px solid #f1f5f9;
                    margin-bottom: 1.5rem; font-family: inherit; resize: none; min-height: 80px;
                }
                .submit-btn {
                    width: 100%; padding: 0.8rem; background: #6366f1; color: white;
                    border: none; border-radius: 12px; font-weight: 700; cursor: pointer;
                    transition: background 0.3s;
                }
                .submit-btn:hover { background: #4f46e5; }
            </style>
        `;

        const div = document.createElement('div');
        div.innerHTML = widgetHtml;
        document.body.appendChild(div);

        const fab = document.getElementById('global-feedback-trigger');
        const modal = document.getElementById('feedback-modal');
        const close = document.getElementById('close-feedback');
        const submit = document.getElementById('submit-modal-feedback');
        const stars = document.querySelectorAll('#modal-stars i');
        let rating = 0;

        const openModal = () => { modal.style.display = 'flex'; };
        const closeModal = () => { modal.style.display = 'none'; sessionStorage.setItem('feedback_prompted', 'true'); };

        fab.addEventListener('click', openModal);
        close.addEventListener('click', closeModal);

        stars.forEach(star => {
            star.addEventListener('click', () => {
                rating = parseInt(star.getAttribute('data-v'));
                stars.forEach((s, i) => s.classList.toggle('active', i < rating));
            });
        });

        submit.addEventListener('click', async () => {
            const message = document.getElementById('modal-message').value;
            const college = document.getElementById('modal-college').value;
            if (!message && rating === 0) return;

            try {
                const res = await fetch('/api/submit_feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ rating, message, college })
                });
                if (res.ok) {
                    submit.textContent = "Thank you! ❤️";
                    submit.style.background = "#22c55e";
                    setTimeout(closeModal, 1500);
                }
            } catch (e) {}
        });

        // Smart Trigger: Show after 3 minutes of activity
        let minutesActive = 0;
        const triggerInterval = setInterval(() => {
            const isTabVisible = document.visibilityState === 'visible';
            const isActive = (Date.now() - lastActivityTime) < ACTIVITY_THRESHOLD;
            if (isTabVisible && isActive) {
                minutesActive++;
                if (minutesActive >= 3) {
                    openModal();
                    clearInterval(triggerInterval);
                }
            }
        }, 60000);
    };

    injectFeedbackWidget();
});
