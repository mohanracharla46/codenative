document.addEventListener('DOMContentLoaded', () => {
    // Background study session logger
    // Tracks study hours for logged in users automatically
    setInterval(async () => {
        try {
            await fetch('/api/log_study', { method: 'POST' });
        } catch (e) {
            // Silently fail if offline or not logged in
        }
    }, 60000); // 1 minute interval
});
