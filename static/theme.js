document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check for saved theme preference
    const currentTheme = localStorage.getItem('theme');

    // Apply theme immediately
    if (currentTheme === 'light') {
        body.classList.add('light-mode');
    } else {
        body.classList.remove('light-mode');
    }

    // Only set up listeners if button exists
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        
        if (currentTheme === 'light' && icon) {
            icon.classList.replace('fa-moon', 'fa-sun');
        } else if (icon) {
            icon.classList.replace('fa-sun', 'fa-moon');
        }

        themeToggle.addEventListener('click', () => {
            body.classList.toggle('light-mode');
            const isLight = body.classList.contains('light-mode');
            
            if (icon) {
                if (isLight) {
                    icon.classList.replace('fa-moon', 'fa-sun');
                    localStorage.setItem('theme', 'light');
                } else {
                    icon.classList.replace('fa-sun', 'fa-moon');
                    localStorage.setItem('theme', 'dark');
                }
            }
            }
        });
    }
    
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
