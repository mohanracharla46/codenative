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
});
