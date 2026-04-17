document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const icon = themeToggle.querySelector('i');

    // Check for saved theme preference
    const currentTheme = localStorage.getItem('theme');

    // Default to dark mode (which is lack of .light-mode class)
    if (currentTheme === 'light') {
        body.classList.add('light-mode');
        icon.classList.replace('fa-moon', 'fa-sun');
    } else {
        // Ensure dark mode is default even if no preference is saved
        body.classList.remove('light-mode');
        icon.classList.replace('fa-sun', 'fa-moon');
    }

    themeToggle.addEventListener('click', () => {
        body.classList.toggle('light-mode');

        const isLight = body.classList.contains('light-mode');

        // Update icon
        if (isLight) {
            icon.classList.replace('fa-moon', 'fa-sun');
            localStorage.setItem('theme', 'light');
        } else {
            icon.classList.replace('fa-sun', 'fa-moon');
            localStorage.setItem('theme', 'dark');
        }
    });
});
