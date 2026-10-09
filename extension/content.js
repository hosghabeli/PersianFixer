// PersianFixer - Content Script (Manifest V3)
// Real-time Persian RTL & Vazirmatn Font Engine for Chrome

(function () {
    const PERSIAN_REGEX = /[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]/;
    const PROSE_LANGS = /^(markdown|md|text|txt|plaintext|plain|raw|prompt|draft|none)$/i;
    const CODE_LANGS = /^(python|py|javascript|js|typescript|ts|jsx|tsx|html|css|scss|c|cpp|csharp|cs|java|go|rust|rs|php|ruby|rb|swift|kotlin|kt|scala|perl|shell|sh|bash|zsh|powershell|ps1|sql|json|yaml|yml|xml|toml|dockerfile|makefile|graphql)/i;
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

/* Strictly Preserve Programming Code Blocks & Terminal as Clean LTR */
pre:not(.persian-code-block):not([dir="rtl"]),
code:not(.persian-code-block):not([dir="rtl"]),
kbd, samp,
pre:not(.persian-code-block):not([dir="rtl"]) *,
code:not(.persian-code-block):not([dir="rtl"]) *,
.monaco-editor, .monaco-editor *,
.code-block:not(.persian-code-block):not([dir="rtl"]),
[data-code-block]:not(.persian-code-block):not([dir="rtl"]),
.font-mono:not(.persian-code-block):not([dir="rtl"]),
[class*="mono"]:not(.persian-code-block):not([dir="rtl"]) {
  direction: ltr !important;
  text-align: left !important;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace !important;
  unicode-bidi: isolate !important;
}

/* Persian Markdown & Prose Code Blocks */
pre.persian-code-block,
pre[dir="rtl"].persian-code-block,
pre.persian-code-block > code,
code.persian-code-block,
code[dir="rtl"].persian-code-block,
.code-block.persian-code-block pre,
.code-block.persian-code-block code,
.code-block[dir="rtl"] pre,
.code-block[dir="rtl"] code,
pre[dir="rtl"] {
  direction: rtl !important;
  text-align: right !important;
  ${forceFont ? "font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;" : ""}
  white-space: pre-wrap !important;
  word-break: break-word !important;
  unicode-bidi: plaintext !important;
}

/* Children of Persian Code Blocks */
pre.persian-code-block *,
code.persian-code-block *,
pre[dir="rtl"] * {
  ${forceFont ? "font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;" : ""}
}

/* Technical inline code, tokens, backticks, IPs, and code syntax inside Persian code blocks */
pre.persian-code-block .hljs-code,
pre.persian-code-block .hljs-literal,
pre.persian-code-block .hljs-link,
pre.persian-code-block .token.code,
code.persian-code-block .hljs-code,
code.persian-code-block .hljs-literal,
code.persian-code-block .token.code,
pre[dir="rtl"] .hljs-code,
pre[dir="rtl"] .token.code {
  direction: ltr !important;
  text-align: left !important;
  display: inline-block !important;
  unicode-bidi: isolate !important;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Courier New", monospace !important;
  font-size: 0.9em !important;
  padding: 0.05em 0.3em !important;
  margin: 0 0.15em !important;
  vertical-align: baseline !important;
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

    function processCodeBlock(el) {
        try {
            if (!el || !(el instanceof HTMLElement)) return;
            if (el.closest('.monaco-editor')) return;

            const tag = el.tagName.toLowerCase();
            if (tag !== 'pre' && tag !== 'code') return;

            const preEl = tag === 'pre' ? el : (el.closest('pre') || el);
            const codeEl = tag === 'code' ? el : (preEl.querySelector('code') || el);

            let lang = '';
            const classNames = ((preEl.className || '') + ' ' + (codeEl.className || ''));
            const langMatch = classNames.match(/(?:language|lang)-([a-z0-9_-]+)/i);
            if (langMatch) {
                lang = langMatch[1].toLowerCase();
            } else {
                const blockParent = preEl.closest('.code-block, [class*="codeBlock"], [class*="code-block"], [data-language]') || preEl.parentElement;
                if (blockParent) {
                    if (blockParent.getAttribute('data-language')) {
                        lang = blockParent.getAttribute('data-language').toLowerCase();
                    } else {
                        const header = blockParent.querySelector && blockParent.querySelector('[class*="header"], [class*="Header"], span, div');
                        if (header && header.textContent) {
                            const firstWord = header.textContent.trim().toLowerCase().split(/\s+/)[0];
                            if (PROSE_LANGS.test(firstWord) || CODE_LANGS.test(firstWord)) {
                                lang = firstWord;
                            }
                        }
                    }
                }
            }

            const text = (codeEl.textContent || preEl.textContent || '');
            const persianMatches = text.match(/[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]/g);
            const persianCount = persianMatches ? persianMatches.length : 0;

            let isPersian = false;
            if (PROSE_LANGS.test(lang)) {
                if (persianCount > 0) isPersian = true;
            } else if (CODE_LANGS.test(lang)) {
                isPersian = false;
            } else {
                const latinMatches = text.match(/[A-Za-z]/g);
                const latinCount = latinMatches ? latinMatches.length : 0;
                if (persianCount >= 15 && (persianCount > latinCount * 0.25 || persianCount > 40)) {
                    isPersian = true;
                }
            }

            const forceFont = currentSettings.forceVazirFont !== false;
            const fontStyle = forceFont ? "'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" : "";

            if (isPersian) {
                if (preEl.getAttribute('dir') !== 'rtl' || !preEl.classList.contains('persian-code-block')) {
                    preEl.classList.add('persian-code-block');
                    preEl.setAttribute('dir', 'rtl');
                    preEl.style.direction = 'rtl';
                    preEl.style.textAlign = 'right';
                    if (fontStyle) preEl.style.fontFamily = fontStyle;
                    preEl.style.whiteSpace = 'pre-wrap';
                    preEl.style.wordBreak = 'break-word';

                    if (codeEl && codeEl !== preEl) {
                        codeEl.classList.add('persian-code-block');
                        codeEl.setAttribute('dir', 'rtl');
                        codeEl.style.direction = 'rtl';
                        codeEl.style.textAlign = 'right';
                        if (fontStyle) codeEl.style.fontFamily = fontStyle;
                        codeEl.style.whiteSpace = 'pre-wrap';
                        codeEl.style.wordBreak = 'break-word';
                        codeEl.style.display = 'block';
                    }

                    const blockContainer = preEl.closest('.code-block, [class*="code-block"]');
                    if (blockContainer && !blockContainer.classList.contains('persian-code-block')) {
                        blockContainer.classList.add('persian-code-block');
                        blockContainer.setAttribute('dir', 'rtl');
                    }
                }
            } else {
                if (preEl.classList.contains('persian-code-block')) {
                    preEl.classList.remove('persian-code-block');
                    preEl.removeAttribute('dir');
                    preEl.style.direction = '';
                    preEl.style.textAlign = '';
                    preEl.style.fontFamily = '';
                    preEl.style.whiteSpace = '';
                    preEl.style.wordBreak = '';

                    if (codeEl && codeEl !== preEl) {
                        codeEl.classList.remove('persian-code-block');
                        codeEl.removeAttribute('dir');
                        codeEl.style.direction = '';
                        codeEl.style.textAlign = '';
                        codeEl.style.fontFamily = '';
                        codeEl.style.whiteSpace = '';
                        codeEl.style.wordBreak = '';
                        codeEl.style.display = '';
                    }
                }
            }
        } catch (e) {}
    }

    function processElement(el) {
        try {
            if (!el || !(el instanceof HTMLElement)) return;

            const tag = el.tagName.toLowerCase();

            // Process code blocks (pre, code)
            if (tag === 'pre' || tag === 'code') {
                processCodeBlock(el);
                return;
            }

            // Skip code blocks, editors, scripts, styles
            if (tag === 'script' || tag === 'style' || el.closest('pre, code, .monaco-editor, .hljs')) {
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
            const targets = document.querySelectorAll('p, li, h1, h2, h3, h4, h5, h6, blockquote, div, th, td, table, textarea, input, [contenteditable="true"], pre, code');
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
