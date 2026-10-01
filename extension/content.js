// PersianFixer - Content Script (Manifest V3)
// Real-time Persian RTL & Vazirmatn Font Engine for Chrome

(function () {
    const PERSIAN_REGEX = /[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]/;
    const STYLE_ID = 'persian-fixer-extension-style';
    
    let isEnabled = false;
    let observer = null;
    let sweepInterval = null;
    let lastRightClickedElement = null;

    // Track right-clicked element for context menu actions
    document.addEventListener('contextmenu', (e) => {
        lastRightClickedElement = e.target;
    }, true);

    // Build the dynamic CSS
    function getCssRules(settings) {
        const fontUrl = chrome.runtime.getURL('fonts/Vazirmatn.ttf');
        const forceFont = settings.forceVazirFont !== false;
        const fontScale = settings.fontSizeDelta ? (1 + settings.fontSizeDelta / 100) : 1;

        return `
@font-face {
  font-family: 'Vazirmatn';
  src: local('Vazirmatn'), local('Vazirmatn-Regular'),
       url('${fontUrl}') format('truetype'),
       url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-Regular.woff2') format('woff2');
  font-weight: normal;
  font-style: normal;
  font-display: swap;
}

/* Global RTL Elements */
[dir="rtl"], .fa-rtl, .persian-text {
  direction: rtl !important;
  text-align: right !important;
  ${forceFont ? "font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;" : ""}
}

/* Persian Paragraphs and Headings */
p[dir="rtl"], h1[dir="rtl"], h2[dir="rtl"], h3[dir="rtl"], h4[dir="rtl"], h5[dir="rtl"], h6[dir="rtl"], blockquote[dir="rtl"] {
  direction: rtl !important;
  text-align: right !important;
  line-height: 1.8 !important;
  ${fontScale !== 1 ? `font-size: ${fontScale}em !important;` : ''}
}

/* Lists and list items in RTL */
ul[dir="rtl"], ol[dir="rtl"], .persian-list, [dir="rtl"] ul, [dir="rtl"] ol {
  direction: rtl !important;
  text-align: right !important;
  padding-right: 1.8rem !important;
  padding-left: 0.5rem !important;
}

li[dir="rtl"], li.persian-text {
  direction: rtl !important;
  text-align: right !important;
  margin-right: 0 !important;
}

/* Strictly Preserve Code Blocks & Terminal as Clean LTR */
pre, code, kbd, samp, pre *, code *,
.monaco-editor, .monaco-editor *,
.code-block, [data-code-block],
.font-mono, [class*="mono"],
.hljs, [class*="language-"] {
  direction: ltr !important;
  text-align: left !important;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace !important;
  unicode-bidi: isolate !important;
}

/* Inline Code inside Persian text */
[dir="rtl"] code, .persian-text code {
  direction: ltr !important;
  display: inline-block !important;
  unicode-bidi: isolate !important;
  font-size: 0.88em !important;
  padding: 0.1em 0.4em !important;
  margin: 0 0.25em !important;
  vertical-align: baseline !important;
}

/* Persian & RTL Markdown Tables */
table[dir="rtl"], table.persian-table, [dir="rtl"] table {
  direction: rtl !important;
  text-align: right !important;
}

table[dir="rtl"] th, table[dir="rtl"] td,
th[dir="rtl"], td[dir="rtl"],
th.persian-text, td.persian-text {
  direction: rtl !important;
  text-align: right !important;
  ${forceFont ? "font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;" : ""}
}

/* Input Fields & Textareas */
textarea.persian-input, input.persian-input, [contenteditable="true"].persian-input {
  direction: rtl !important;
  text-align: right !important;
  ${forceFont ? "font-family: 'Vazirmatn', sans-serif !important;" : ""}
}
`;
    }

    function injectStyle(targetDoc, settings) {
        try {
            if (!targetDoc) return;
            const root = targetDoc.head || targetDoc.documentElement || targetDoc;
            if (!root || !root.appendChild) return;

            let existing = root.querySelector ? root.querySelector(`#${STYLE_ID}`) : null;
            if (!existing) {
                const style = targetDoc.createElement('style');
                style.id = STYLE_ID;
                style.textContent = getCssRules(settings);
                root.appendChild(style);
            } else {
                existing.textContent = getCssRules(settings);
            }
        } catch (e) {}
    }

    function removeStyle(targetDoc) {
        try {
            if (!targetDoc) return;
            const root = targetDoc.head || targetDoc.documentElement || targetDoc;
            const existing = root?.querySelector ? root.querySelector(`#${STYLE_ID}`) : null;
            if (existing) existing.remove();
        } catch (e) {}
    }

    function processElement(el) {
        try {
            if (!el || !(el instanceof HTMLElement)) return;

            const tag = el.tagName.toLowerCase();

            // Skip code blocks, editors, scripts, styles
            if (tag === 'pre' || tag === 'code' || tag === 'script' || tag === 'style' || el.closest('pre, code, .monaco-editor, .hljs')) {
                return;
            }

            // Pierce open shadow roots (crucial for modern web components)
            if (el.shadowRoot) {
                injectStyle(el.shadowRoot, currentSettings);
                const shadowChildren = el.shadowRoot.querySelectorAll('*');
                for (let j = 0; j < shadowChildren.length; j++) {
                    processElement(shadowChildren[j]);
                }
            }

            // Input elements & contenteditables
            if (tag === 'textarea' || tag === 'input' || el.isContentEditable) {
                const val = el.value !== undefined ? el.value : (el.textContent || '');
                const trimmed = val.trim();
                if (trimmed.length > 0) {
                    const firstChar = trimmed.match(/[A-Za-z\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF]/);
                    if (firstChar && PERSIAN_REGEX.test(firstChar[0])) {
                        if (el.getAttribute('dir') !== 'rtl') {
                            el.setAttribute('dir', 'rtl');
                            el.classList.add('persian-input');
                            el.style.direction = 'rtl';
                            el.style.textAlign = 'right';
                        }
                        return;
                    }
                }
                if (el.classList.contains('persian-input')) {
                    el.classList.remove('persian-input');
                    el.setAttribute('dir', 'ltr');
                    el.style.direction = 'ltr';
                    el.style.textAlign = 'left';
                }
                return;
            }

            // Block-level text elements & tables:
            // p, li, h1..h6, blockquote, div, th, td, table
            if (/^(p|li|h1|h2|h3|h4|h5|h6|blockquote|div|th|td|table)$/i.test(tag)) {
                let containsPersian = false;

                // 1. Direct text nodes check (fastest)
                for (let child = el.firstChild; child; child = child.nextSibling) {
                    if (child.nodeType === 3) {
                        const text = child.nodeValue;
                        if (text && PERSIAN_REGEX.test(text)) {
                            containsPersian = true;
                            break;
                        }
                    }
                }

                // 2. Full text fallback for block elements
                if (!containsPersian && /^(p|li|h1|h2|h3|h4|h5|h6|blockquote|th|td|table)$/i.test(tag)) {
                    const text = el.innerText || el.textContent || '';
                    if (text && PERSIAN_REGEX.test(text)) {
                        containsPersian = true;
                    }
                }

                if (containsPersian) {
                    if (el.getAttribute('dir') !== 'rtl') {
                        el.setAttribute('dir', 'rtl');
                        el.classList.add(tag === 'table' ? 'persian-table' : 'persian-text');
                        el.style.direction = 'rtl';
                        el.style.textAlign = 'right';

                        // If li, also set list to rtl
                        if (tag === 'li' && el.parentElement && /^(ul|ol)$/i.test(el.parentElement.tagName)) {
                            el.parentElement.setAttribute('dir', 'rtl');
                            el.parentElement.classList.add('persian-list');
                            el.parentElement.style.direction = 'rtl';
                            el.parentElement.style.textAlign = 'right';
                        }

                        // If th or td, make sure parent table is RTL so columns order RTL
                        if (tag === 'th' || tag === 'td') {
                            const tbl = el.closest ? el.closest('table') : null;
                            if (tbl && tbl.getAttribute('dir') !== 'rtl') {
                                tbl.setAttribute('dir', 'rtl');
                                tbl.classList.add('persian-table');
                                tbl.style.direction = 'rtl';
                                tbl.style.textAlign = 'right';
                            }
                        }
                    }
                }
            }
        } catch (err) {}
    }

    function scanAll() {
        if (!isEnabled) return;
        try {
            injectStyle(document, currentSettings);
            const targets = document.querySelectorAll('p, li, h1, h2, h3, h4, h5, h6, blockquote, div, th, td, table, textarea, input, [contenteditable="true"]');
            for (let i = 0; i < targets.length; i++) {
                processElement(targets[i]);
            }
        } catch (e) {}
    }

    let isScheduled = false;
    function scheduleScan() {
        if (isScheduled || !isEnabled) return;
        isScheduled = true;
        requestAnimationFrame(() => {
            isScheduled = false;
            scanAll();
        });
    }

    let currentSettings = {};

    const KNOWN_AI_DOMAINS = [
        'chatgpt.com',
        'openai.com',
        'claude.ai',
        'gemini.google.com',
        'aistudio.google.com',
        'deepseek.com',
        'perplexity.ai',
        'poe.com',
        'copilot.microsoft.com',
        'mistral.ai',
        'groq.com',
        'v0.dev',
        'huggingface.co'
    ];

    function shouldRun(settings) {
        if (!settings || settings.enabled === false) return false;

        const hostname = window.location.hostname.toLowerCase();
        
        // Safety guard: Never touch Gmail, Docs, YouTube or internal search
        if (hostname.includes('mail.google.com') || hostname.includes('youtube.com') || hostname.includes('docs.google.com')) {
            return false;
        }

        // Check blacklist
        const blacklist = settings.blacklist || [];
        if (blacklist.some(b => hostname === b.toLowerCase() || hostname.endsWith('.' + b.toLowerCase()))) {
            return false;
        }

        // Default mode is strictly ai_only
        const mode = settings.mode || 'ai_only';
        if (mode === 'ai_only') {
            const aiDomains = (settings.aiDomains && settings.aiDomains.length > 0) ? settings.aiDomains : KNOWN_AI_DOMAINS;
            return aiDomains.some(d => hostname.includes(d.toLowerCase()));
        }

        return true;
    }

    function startEngine() {
        if (isEnabled) return;
        isEnabled = true;
        scanAll();

        try {
            observer = new MutationObserver(() => {
                scheduleScan();
            });
            const root = document.body || document.documentElement;
            if (root) {
                observer.observe(root, { childList: true, subtree: true, characterData: true });
            }
        } catch (e) {}

        // Streaming sweep every 600ms
        sweepInterval = setInterval(() => {
            scanAll();
        }, 600);

        chrome.runtime.sendMessage({ action: 'check-status', isActive: true }).catch(() => {});
    }

    function stopEngine() {
        isEnabled = false;
        if (observer) {
            observer.disconnect();
            observer = null;
        }
        if (sweepInterval) {
            clearInterval(sweepInterval);
            sweepInterval = null;
        }
        removeStyle(document);
        chrome.runtime.sendMessage({ action: 'check-status', isActive: false }).catch(() => {});
    }

    function init() {
        chrome.storage.sync.get(null, (settings) => {
            currentSettings = settings || {};
            if (shouldRun(currentSettings)) {
                startEngine();
            } else {
                stopEngine();
            }
        });
    }

    // Message listener
    chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
        if (msg.action === 'settings-updated') {
            chrome.storage.sync.get(null, (settings) => {
                currentSettings = settings || {};
                if (shouldRun(currentSettings)) {
                    startEngine();
                    scanAll();
                } else {
                    stopEngine();
                }
            });
            sendResponse({ success: true });
        } else if (msg.action === 'toggle-selected-rtl') {
            const target = lastRightClickedElement || document.activeElement;
            if (target && target instanceof HTMLElement) {
                const currentDir = target.getAttribute('dir') || window.getComputedStyle(target).direction;
                const newDir = currentDir === 'rtl' ? 'ltr' : 'rtl';
                target.setAttribute('dir', newDir);
                target.style.direction = newDir;
                target.style.textAlign = newDir === 'rtl' ? 'right' : 'left';
            }
            sendResponse({ success: true });
        }
    });

    // Start on DOM ready or immediate
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
