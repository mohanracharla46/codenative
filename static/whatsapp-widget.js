/**
 * CodeNative WhatsApp Channel Floating Widget
 * Auto-injects a premium floating button on the bottom-left linking to the WhatsApp channel.
 */
(function () {
    function initWhatsAppWidget() {
        // Check if dismissed
        if (localStorage.getItem('cn_whatsapp_widget_dismissed') === 'true') {
            return;
        }

        const CHANNEL_URL = 'https://whatsapp.com/channel/0029Vb7lp702P59gBIjIhx0O';

        // Inject CSS styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes wa-pulse {
                0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.5); }
                50% { transform: scale(1.08); box-shadow: 0 0 0 12px rgba(37, 211, 102, 0); }
            }
            @keyframes wa-bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-6px); }
            }
            
            #wa-widget-container {
                position: fixed;
                bottom: 28px;
                left: 28px;
                z-index: 9999;
                display: flex;
                align-items: center;
                font-family: 'Inter', sans-serif;
            }
            
            #wa-fab {
                width: 56px;
                height: 56px;
                border-radius: 50%;
                background: #25D366;
                color: #fff;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                text-decoration: none;
                box-shadow: 0 8px 24px rgba(37, 211, 102, 0.4);
                animation: wa-pulse 3s ease-in-out infinite;
                transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                position: relative;
            }
            
            #wa-fab:hover {
                transform: scale(1.1) rotate(8deg);
                background: #20ba5a;
            }
            
            #wa-close-btn {
                position: absolute;
                top: -5px;
                right: -5px;
                width: 18px;
                height: 18px;
                border-radius: 50%;
                background: #ef4444;
                color: #fff;
                border: 1px solid #fff;
                font-size: 11px;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                transition: transform 0.2s;
                z-index: 10;
            }
            
            #wa-close-btn:hover {
                transform: scale(1.2);
            }
            
            #wa-tooltip {
                margin-left: 12px;
                background: #1e293b;
                color: #fff;
                padding: 8px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                white-space: nowrap;
                pointer-events: none;
                position: relative;
                animation: wa-bounce 4s infinite;
                border: 1px solid rgba(255,255,255,0.08);
            }
            
            #wa-tooltip::before {
                content: '';
                position: absolute;
                left: -6px;
                top: 50%;
                transform: translateY(-50%);
                border-top: 6px solid transparent;
                border-bottom: 6px solid transparent;
                border-right: 6px solid #1e293b;
            }

            @media (max-width: 768px) {
                #wa-widget-container {
                    bottom: 20px;
                    left: 20px;
                }
                #wa-tooltip {
                    display: none; /* Hide tooltip on small mobile screens */
                }
            }
        `;
        document.head.appendChild(style);

        // Create Widget DOM Elements
        const container = document.createElement('div');
        container.id = 'wa-widget-container';

        const fab = document.createElement('a');
        fab.id = 'wa-fab';
        fab.href = CHANNEL_URL;
        fab.target = '_blank';
        fab.rel = 'noopener noreferrer';
        fab.setAttribute('aria-label', 'Join WhatsApp Channel');
        fab.innerHTML = '<i class="fab fa-whatsapp"></i>';

        const closeBtn = document.createElement('div');
        closeBtn.id = 'wa-close-btn';
        closeBtn.innerHTML = '&times;';
        closeBtn.title = 'Dismiss';
        closeBtn.setAttribute('role', 'button');
        closeBtn.setAttribute('tabindex', '0');
        closeBtn.setAttribute('aria-label', 'Dismiss WhatsApp widget');
        closeBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            container.style.display = 'none';
            localStorage.setItem('cn_whatsapp_widget_dismissed', 'true');
        });

        const tooltip = document.createElement('div');
        tooltip.id = 'wa-tooltip';
        tooltip.textContent = 'Get Job & Class Updates! 📢';

        fab.appendChild(closeBtn);
        container.appendChild(fab);
        container.appendChild(tooltip);
        document.body.appendChild(container);
    }

    if (window.requestIdleCallback) {
        window.requestIdleCallback(initWhatsAppWidget, { timeout: 2500 });
    } else if (document.readyState === 'complete') {
        initWhatsAppWidget();
    } else {
        window.addEventListener('load', initWhatsAppWidget, { passive: true });
    }
})();
