/**
 * CodeNative Tutorial Loader
 * Centralized logic for dynamic content loading, progress tracking, and UI interactions.
 */

const TutorialLoader = {
    config: {
        lang: '',
        isLoggedIn: false,
        lessonCache: {},
        sidebarTopics: null,
        contentBox: null,
        editor: null
    },

    init(options) {
        this.config = { ...this.config, ...options };
        this.config.sidebarTopics = document.getElementById('sidebarTopics');
        this.config.contentBox = document.getElementById('topicContent');
        
        this.setupNavigation();
        this.setupSidebar();
        this.loadTopics();
        
        // Handle initial URL hash if any (for deep linking)
        const hash = window.location.hash.replace('#', '');
        if (hash) {
            // We'll handle this after topics are loaded
            this.config.initialSlug = hash;
        }
    },

    setupNavigation() {
        const prevBtn = document.getElementById('prevTopic');
        const nextBtn = document.getElementById('nextTopic');
        
        if (prevBtn) {
            prevBtn.onclick = () => {
                const active = document.querySelector('.topic.active');
                if (active && active.previousElementSibling) active.previousElementSibling.click();
            };
        }
        
        if (nextBtn) {
            nextBtn.onclick = () => {
                const active = document.querySelector('.topic.active');
                if (active && active.nextElementSibling) active.nextElementSibling.click();
            };
        }
    },

    setupSidebar() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebarClose = document.getElementById('sidebarClose');
        const sidebar = document.querySelector('.tutorial-sidebar');
        const menuIcon = sidebarToggle ? sidebarToggle.querySelector('i') : null;

        const toggle = (e) => {
            if (e) e.stopPropagation();
            sidebar.classList.toggle('active');
            if (menuIcon) {
                if (sidebar.classList.contains('active')) {
                    menuIcon.classList.replace('fa-bars', 'fa-times');
                } else {
                    menuIcon.classList.replace('fa-times', 'fa-bars');
                }
            }
            if (this.config.editor) {
                setTimeout(() => this.config.editor.resize(), 300);
            }
        };

        if (sidebarToggle) sidebarToggle.addEventListener('click', toggle);
        if (sidebarClose) sidebarClose.addEventListener('click', toggle);

        document.addEventListener('click', (e) => {
            if (sidebar && sidebar.classList.contains('active')) {
                if (!sidebar.contains(e.target) && e.target !== sidebarToggle) {
                    sidebar.classList.remove('active');
                    if (menuIcon) menuIcon.classList.replace('fa-times', 'fa-bars');
                }
            }
        });

        if (this.config.sidebarTopics) {
            this.config.sidebarTopics.addEventListener("click", (e) => {
                const topicEl = e.target.closest('.topic');
                if (topicEl && window.innerWidth <= 1024) {
                    sidebar.classList.remove("active");
                    if (menuIcon) menuIcon.classList.replace('fa-times', 'fa-bars');
                }
            });
        }
    },

    async loadTopics() {
        const { lang, sidebarTopics } = this.config;
        const cacheKey = `topics_${lang}`;
        const cachedTopics = localStorage.getItem(cacheKey);

        // 1. Show cached topics immediately
        if (cachedTopics) {
            try {
                this.renderTopics(JSON.parse(cachedTopics));
            } catch (e) {
                localStorage.removeItem(cacheKey);
            }
        } else {
            // Show skeleton if no cache
            this.showSidebarSkeleton();
        }

        // 2. Fetch fresh data from API (Stale-While-Revalidate)
        try {
            const res = await fetch(`/api/content/${lang}`);
            if (!res.ok) throw new Error('Failed to fetch topics');
            
            const topics = await res.json();
            if (topics && Array.isArray(topics) && topics.length > 0) {
                localStorage.setItem(cacheKey, JSON.stringify(topics));
                this.renderTopics(topics);
            } else if (topics && Array.isArray(topics) && topics.length === 0) {
                // Handle truly empty content (could be DB issue or fallback to empty SQLite)
                this.showEmptySidebar();
            }
        } catch (err) {
            console.error('Tutorial Error:', err);
            if (!cachedTopics) {
                this.showSidebarError();
            }
        }
    },

    showSidebarError() {
        if (!this.config.sidebarTopics) return;
        this.config.sidebarTopics.innerHTML = `
            <div style="padding: 20px; text-align: center; color: #ef4444;">
                <i class="fas fa-exclamation-circle" style="font-size: 24px; margin-bottom: 10px;"></i>
                <p style="font-size: 13px; font-weight: 600;">Failed to load lessons.</p>
                <button onclick="location.reload()" style="margin-top: 10px; padding: 5px 15px; border-radius: 6px; border: 1px solid #ef4444; background: transparent; color: #ef4444; font-size: 12px; cursor: pointer;">Retry</button>
            </div>
        `;
    },

    showEmptySidebar() {
        if (!this.config.sidebarTopics) return;
        this.config.sidebarTopics.innerHTML = `
            <div style="padding: 20px; text-align: center; color: #64748b;">
                <i class="fas fa-folder-open" style="font-size: 24px; margin-bottom: 10px; opacity: 0.5;"></i>
                <p style="font-size: 13px; font-weight: 600;">No lessons found.</p>
                <button onclick="TutorialLoader.clearCacheAndReload()" style="margin-top: 10px; padding: 5px 15px; border-radius: 6px; border: 1px solid #64748b; background: transparent; color: #64748b; font-size: 12px; cursor: pointer;">Refresh Source</button>
            </div>
        `;
    },

    clearCacheAndReload() {
        const { lang } = this.config;
        localStorage.removeItem(`topics_${lang}`);
        location.reload();
    },

    renderTopics(topics) {
        const { sidebarTopics, isLoggedIn, initialSlug } = this.config;
        
        if (!topics || topics.length === 0) {
            this.showEmptySidebar();
            return;
        }

        sidebarTopics.innerHTML = '';
        topics.forEach((topic, index) => {
            const li = document.createElement('li');
            li.className = `topic ${topic.completed ? 'completed' : ''}`;
            li.dataset.topic = topic.topic_slug;
            li.dataset.index = index;
            
            let lockIcon = '';
            if (!isLoggedIn && index > 0) {
                lockIcon = '<i class="fas fa-lock" style="margin-right: 8px; font-size: 11px; opacity: 0.5;"></i>';
            }

            li.innerHTML = `
                ${topic.completed ? '<i class="fas fa-check-circle completion-mark"></i>' : ''}
                <div class="topic-indicator"></div>
                ${lockIcon}
                <span class="topic-title">${topic.topic_title}</span>
            `;
            
            li.onclick = () => {
                if (!isLoggedIn && index > 0) {
                    window.location.href = `/signin.html?next=${encodeURIComponent(window.location.pathname)}&error=login_required`;
                    return;
                }
                this.loadSpecificTopic(topic.topic_slug, li);
            };
            sidebarTopics.appendChild(li);
        });

        // Determine which topic to load initially
        let topicToLoad = topics[0].topic_slug;
        let elementToLoad = sidebarTopics.firstChild;

        if (initialSlug) {
            const found = topics.find(t => t.topic_slug === initialSlug);
            if (found) {
                topicToLoad = found.topic_slug;
                elementToLoad = sidebarTopics.querySelector(`[data-topic="${initialSlug}"]`);
            }
            this.config.initialSlug = null; // Clear it
        }

        if (elementToLoad) {
            this.loadSpecificTopic(topicToLoad, elementToLoad);
        }
    },

    async loadSpecificTopic(slug, el) {
        const { lang, lessonCache, contentBox, isLoggedIn } = this.config;
        
        try {
            const topicIndex = el ? parseInt(el.dataset.index) : 0;
            
            // UI state update
            document.querySelectorAll('.topic').forEach(t => t.classList.remove('active'));
            if (el) el.classList.add('active');
            
            // Update URL hash without jumping
            history.replaceState(null, null, `#${slug}`);

            // Show loading state if not cached
            if (!lessonCache[slug]) {
                this.showContentLoading();
            }

            // Fetch from cache or API
            let data;
            if (lessonCache[slug]) {
                data = lessonCache[slug];
            } else {
                const res = await fetch(`/api/content/${lang}/${slug}`);
                if (!res.ok) throw new Error('Content fetch failed');
                data = await res.json();
                lessonCache[slug] = data;
            }

            // Clean up custom assets from previous lesson
            document.querySelectorAll('.custom-lesson-asset').forEach(asset => asset.remove());

            if (data.content_html) {
                contentBox.innerHTML = data.content_html;
            }

            // Apply custom styles/scripts if any
            this.applyCustomAssets(data);

            // Update Next Lesson UI
            this.updateNextLessonBar(el);

            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Save progress
            if (isLoggedIn) {
                this.markTopicComplete(slug, el);
            }

        } catch (err) {
            console.error('Topic Load Error:', err);
            contentBox.innerHTML = `
                <div style="padding: 100px; text-align: center; color: #64748b;">
                    <i class="fas fa-wifi-slash" style="font-size: 48px; margin-bottom: 20px; opacity: 0.3;"></i>
                    <h3>Something went wrong</h3>
                    <p>We couldn't load this lesson. Please check your connection.</p>
                    <button onclick="location.reload()" class="btn-nav-control" style="margin-top: 20px; background: #6366f1; color: white; border: none; padding: 10px 25px; border-radius: 8px; cursor: pointer;">
                        Try Again
                    </button>
                </div>
            `;
        }
    },

    async markTopicComplete(slug, el) {
        try {
            const res = await fetch('/api/complete_topic', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: this.config.lang, topic_slug: slug })
            });

            if (res.ok && el) {
                el.classList.add('completed');
                if (!el.querySelector('.completion-mark')) {
                    el.insertAdjacentHTML('afterbegin', '<i class="fas fa-check-circle completion-mark"></i>');
                }
                
                // Trigger feedback popup if 1st or 2nd lesson
                const completedCount = document.querySelectorAll('.topic.completed').length;
                if (completedCount === 1 || completedCount === 2) {
                    if (typeof FeedbackSystem !== 'undefined') FeedbackSystem.showPrompt();
                }
            }
        } catch (e) { console.error('Progress update failed'); }
    },

    updateNextLessonBar(currentEl) {
        const nextEl = currentEl ? currentEl.nextElementSibling : null;
        const nextBar = document.getElementById('nextLessonBar');
        if (!nextBar) return;

        if (nextEl && nextEl.classList.contains('topic')) {
            nextBar.style.display = 'flex';
            const nextTitle = nextEl.querySelector('.topic-title').textContent;
            const titleEl = nextBar.querySelector('h3');
            if (titleEl) titleEl.textContent = nextTitle;
            
            nextBar.onclick = () => nextEl.click();
        } else {
            nextBar.style.display = 'none';
        }
    },

    applyCustomAssets(data) {
        if (data.custom_css) {
            const style = document.createElement('style');
            style.className = 'custom-lesson-asset';
            style.textContent = data.custom_css;
            document.head.appendChild(style);
        }
        if (data.custom_js) {
            const script = document.createElement('script');
            script.className = 'custom-lesson-asset';
            script.textContent = `(function() { ${data.custom_js} })();`;
            document.body.appendChild(script);
        }
    },

    showSidebarSkeleton() {
        if (!this.config.sidebarTopics) return;
        this.config.sidebarTopics.innerHTML = `
            <div class="sidebar-skeleton">
                <div class="skeleton-item"></div>
                <div class="skeleton-item"></div>
                <div class="skeleton-item"></div>
                <div class="skeleton-item"></div>
                <div class="skeleton-item"></div>
            </div>
        `;
    },

    showContentLoading() {
        if (!this.config.contentBox) return;
        const icon = this.config.lang === 'python' ? 'fab fa-python' : 
                   this.config.lang === 'java' ? 'fab fa-java' : 
                   this.config.lang === 'c' ? 'fas fa-code-branch' : 'fas fa-book-open';
        
        const color = this.config.lang === 'python' ? '#3776ab' : 
                    this.config.lang === 'java' ? '#ed8b00' : 
                    this.config.lang === 'c' ? '#00599c' : '#6366f1';

        this.config.contentBox.innerHTML = `
            <div style="padding: 100px; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <i class="${icon} fa-beat-fade" style="font-size: 54px; color: ${color}; margin-bottom: 20px;"></i>
                <p style="font-weight: 700; color: #64748b; letter-spacing: 1px; text-transform: uppercase; font-size: 13px;">Linking Lesson...</p>
            </div>
        `;
    }
/**
 * Feedback System - Handles proactive feedback prompts
 */
const FeedbackSystem = {
    showPrompt() {
        // Don't show if already given feedback in this session or recently
        if (localStorage.getItem('feedback_submitted') || sessionStorage.getItem('feedback_dismissed')) {
            return;
        }

        // Delay slightly for better UX
        setTimeout(() => {
            this.injectModal();
        }, 1500);
    },

    injectModal() {
        if (document.getElementById('feedbackModal')) return;

        const modalHtml = `
        <div id="feedbackModal" class="feedback-overlay">
            <div class="feedback-card">
                <button class="feedback-close" onclick="FeedbackSystem.dismiss()">&times;</button>
                <div class="feedback-header">
                    <div class="feedback-icon-wrapper">
                        <i class="fas fa-star fa-beat"></i>
                    </div>
                    <h3>Enjoying Code Native?</h3>
                    <p>You've just finished a lesson! How would you rate your experience so far?</p>
                </div>
                
                <div class="feedback-rating">
                    <span class="star" data-value="1"><i class="fas fa-star"></i></span>
                    <span class="star" data-value="2"><i class="fas fa-star"></i></span>
                    <span class="star" data-value="3"><i class="fas fa-star"></i></span>
                    <span class="star" data-value="4"><i class="fas fa-star"></i></span>
                    <span class="star" data-value="5"><i class="fas fa-star"></i></span>
                </div>

                <div id="feedbackCommentArea" style="display: none; margin-top: 20px;">
                    <textarea id="feedbackMessage" placeholder="Any suggestions to make it better for you? (Optional)" class="feedback-textarea"></textarea>
                    <button id="submitFeedbackBtn" class="feedback-submit-btn" onclick="FeedbackSystem.submit()">Submit Feedback</button>
                </div>
                
                <div class="feedback-footer">
                    <button class="btn-later" onclick="FeedbackSystem.dismiss()">Maybe later</button>
                </div>
            </div>
        </div>`;

        const style = document.createElement('style');
        style.textContent = `
            .feedback-overlay {
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(8px);
                z-index: 9999; display: flex; align-items: center; justify-content: center;
                animation: fadeIn 0.3s ease;
            }
            .feedback-card {
                background: white; width: 100%; max-width: 420px; padding: 40px;
                border-radius: 28px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                position: relative; text-align: center; animation: slideUp 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }
            .feedback-close {
                position: absolute; top: 20px; right: 20px; background: none; border: none;
                font-size: 24px; color: #94a3b8; cursor: pointer; transition: 0.2s;
            }
            .feedback-close:hover { color: #1e293b; transform: scale(1.1); }
            .feedback-icon-wrapper {
                width: 70px; height: 70px; background: #eef2ff; color: #6366f1;
                border-radius: 20px; display: flex; align-items: center; justify-content: center;
                font-size: 30px; margin: 0 auto 24px; transform: rotate(-5deg);
            }
            .feedback-header h3 { font-size: 24px; font-weight: 800; color: #1e293b; margin-bottom: 12px; }
            .feedback-header p { font-size: 15px; color: #64748b; line-height: 1.5; }
            .feedback-rating { display: flex; justify-content: center; gap: 12px; margin-top: 30px; }
            .star { font-size: 32px; color: #e2e8f0; cursor: pointer; transition: all 0.2s; }
            .star:hover { transform: scale(1.2); color: #f59e0b; }
            .star.active { color: #f59e0b; }
            .feedback-textarea {
                width: 100%; height: 100px; border: 1px solid #e2e8f0; border-radius: 16px;
                padding: 16px; font-family: inherit; font-size: 14px; margin-bottom: 20px;
                resize: none; outline: none; transition: 0.2s;
            }
            .feedback-textarea:focus { border-color: #6366f1; box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1); }
            .feedback-submit-btn {
                width: 100%; background: #6366f1; color: white; border: none;
                padding: 14px; border-radius: 16px; font-weight: 700; font-size: 15px;
                cursor: pointer; transition: 0.3s;
            }
            .feedback-submit-btn:hover { background: #4f46e5; transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.3); }
            .feedback-footer { margin-top: 24px; }
            .btn-later { background: none; border: none; color: #94a3b8; font-size: 14px; font-weight: 600; cursor: pointer; }
            .btn-later:hover { color: #64748b; text-decoration: underline; }
            @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            @keyframes slideUp { from { opacity: 0; transform: translateY(40px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
        `;
        document.head.appendChild(style);
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Star logic
        let selectedRating = 0;
        const stars = document.querySelectorAll('.star');
        stars.forEach(star => {
            star.addEventListener('click', () => {
                selectedRating = star.dataset.value;
                stars.forEach(s => {
                    s.classList.toggle('active', s.dataset.value <= selectedRating);
                });
                document.getElementById('feedbackCommentArea').style.display = 'block';
            });
        });

        this.selectedRatingValue = () => selectedRating;
    },

    dismiss() {
        const modal = document.getElementById('feedbackModal');
        if (modal) {
            modal.style.opacity = '0';
            setTimeout(() => modal.remove(), 300);
        }
        sessionStorage.setItem('feedback_dismissed', 'true');
    },

    async submit() {
        const rating = this.selectedRatingValue();
        const message = document.getElementById('feedbackMessage').value;
        const submitBtn = document.getElementById('submitFeedbackBtn');

        if (!rating) return;

        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';

            const res = await fetch('/api/submit_feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rating: rating,
                    message: message,
                    name: 'Tutorial User',
                    email: '',
                    college: ''
                })
            });

            if (res.ok) {
                const card = document.querySelector('.feedback-card');
                card.innerHTML = `
                    <div class="feedback-success">
                        <div class="feedback-icon-wrapper" style="background: #ecfdf5; color: #10b981;">
                            <i class="fas fa-check"></i>
                        </div>
                        <h3>Thank You!</h3>
                        <p>Your feedback helps us make Code Native better for everyone.</p>
                        <button class="feedback-submit-btn" style="margin-top: 24px;" onclick="FeedbackSystem.dismiss()">Close</button>
                    </div>
                `;
                localStorage.setItem('feedback_submitted', 'true');
            }
        } catch (err) {
            console.error('Feedback error:', err);
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit Feedback';
        }
    }
};
