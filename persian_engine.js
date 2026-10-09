// ==UserScript==
// @name         Persian RTL & Vazirmatn Engine v3
// @description  Bulletproof RTL & Vazirmatn engine with SVG isolation and crash-proof observer
// @version      3.0
// ==/UserScript==

(function () {
    const PERSIAN_REGEX = /[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]/;
    const PROSE_LANGS = /^(markdown|md|text|txt|plaintext|plain|raw|prompt|draft|none)$/i;
    const CODE_LANGS = /^(python|py|javascript|js|typescript|ts|jsx|tsx|html|css|scss|c|cpp|csharp|cs|java|go|rust|rs|php|ruby|rb|swift|kotlin|kt|scala|perl|shell|sh|bash|zsh|powershell|ps1|sql|json|yaml|yml|xml|toml|dockerfile|makefile|graphql)/i;

    const CSS = `
@font-face {
  font-family: 'Vazirmatn';
  src: local('Vazirmatn'), local('Vazirmatn Regular'), local('Vazirmatn-Regular'),
       url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
}
@font-face {
  font-family: 'Vazirmatn';
  src: local('Vazirmatn Medium'), local('Vazirmatn-Medium'),
       url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-Medium.woff2') format('woff2');
  font-weight: 500;
  font-style: normal;
}
@font-face {
  font-family: 'Vazirmatn';
  src: local('Vazirmatn Bold'), local('Vazirmatn-Bold'),
       url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-Bold.woff2') format('woff2');
  font-weight: 700;
  font-style: normal;
}

/* Global Font Override for Persian */
body, [class*="message"], [class*="chat"], [class*="prose"], [class*="content"] {
  font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* Base RTL Elements */
[dir="rtl"], .fa-rtl, .persian-text {
  direction: rtl !important;
  text-align: right !important;
  font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
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

/* Preserve Programming Code Blocks & Terminal as Clean LTR */
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
  font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  white-space: pre-wrap !important;
  word-break: break-word !important;
  unicode-bidi: plaintext !important;
}

/* Children of Persian Code Blocks */
pre.persian-code-block *,
code.persian-code-block *,
pre[dir="rtl"] * {
  font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
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

/* Persian & RTL Tables */
table[dir="rtl"], table.persian-table, [dir="rtl"] table {
  direction: rtl !important;
  text-align: right !important;
}

table[dir="rtl"] th, table[dir="rtl"] td,
th[dir="rtl"], td[dir="rtl"],
th.persian-text, td.persian-text {
  direction: rtl !important;
  text-align: right !important;
  font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* Inline Code inside Persian sentences */
[dir="rtl"] code, .persian-text code {
  direction: ltr !important;
  display: inline-block !important;
  unicode-bidi: isolate !important;
  font-size: 0.88em !important;
  padding: 0.1em 0.4em !important;
  margin: 0 0.25em !important;
}

/* Input Fields */
textarea.persian-input, input.persian-input, [contenteditable="true"].persian-input {
  direction: rtl !important;
  text-align: right !important;
  font-family: 'Vazirmatn', sans-serif !important;
}
`;

    function injectStyle(targetDoc) {
        try {
            if (!targetDoc) return;
            const root = targetDoc.head || targetDoc.documentElement || targetDoc;
            if (!root || !root.appendChild) return;
            if (root.querySelector && root.querySelector('#persian-fixer-style')) return;
            const style = targetDoc.createElement('style');
            style.id = 'persian-fixer-style';
            style.textContent = CSS;
            root.appendChild(style);
        } catch (e) {}
    }

    function processCodeBlock(el) {
        try {
            if (!el || !(el instanceof HTMLElement)) return;
            // Never touch monaco editor internals
            if (el.closest('.monaco-editor')) return;

            const tag = el.tagName.toLowerCase();
            if (tag !== 'pre' && tag !== 'code') return;

            // If it's code inside pre, resolve primary container
            const preEl = tag === 'pre' ? el : (el.closest('pre') || el);
            const codeEl = tag === 'code' ? el : (preEl.querySelector('code') || el);

            // Determine language from class names or surrounding code block headers
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
                // If explicitly markdown or prose text, any Persian text triggers RTL
                if (persianCount > 0) isPersian = true;
            } else if (CODE_LANGS.test(lang)) {
                // Programming languages stay LTR
                isPersian = false;
            } else {
                // Unknown/unspecified language: check Persian presence
                const latinMatches = text.match(/[A-Za-z]/g);
                const latinCount = latinMatches ? latinMatches.length : 0;
                if (persianCount >= 15 && (persianCount > latinCount * 0.25 || persianCount > 40)) {
                    isPersian = true;
                }
            }

            if (isPersian) {
                if (preEl.getAttribute('dir') !== 'rtl' || !preEl.classList.contains('persian-code-block')) {
                    preEl.classList.add('persian-code-block');
                    preEl.setAttribute('dir', 'rtl');
                    preEl.style.direction = 'rtl';
                    preEl.style.textAlign = 'right';
                    preEl.style.fontFamily = "'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
                    preEl.style.whiteSpace = 'pre-wrap';
                    preEl.style.wordBreak = 'break-word';

                    if (codeEl && codeEl !== preEl) {
                        codeEl.classList.add('persian-code-block');
                        codeEl.setAttribute('dir', 'rtl');
                        codeEl.style.direction = 'rtl';
                        codeEl.style.textAlign = 'right';
                        codeEl.style.fontFamily = "'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
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

    function processSingleElement(el) {
        try {
            if (!el || !(el instanceof HTMLElement)) return;

            const tag = el.tagName.toLowerCase();

            // Process code elements (pre, code)
            if (tag === 'pre' || tag === 'code') {
                processCodeBlock(el);
                return;
            }

            // Skip script, style, monaco-editor, and elements inside code blocks
            if (tag === 'script' || tag === 'style' || el.closest('pre, code, .monaco-editor')) {
                return;
            }

            // Pierce open shadow root
            if (el.shadowRoot) {
                injectStyle(el.shadowRoot);
                const shadowChildren = el.shadowRoot.querySelectorAll('*');
                for (let j = 0; j < shadowChildren.length; j++) {
                    processSingleElement(shadowChildren[j]);
                }
            }

            // Input handling
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
                            el.style.fontFamily = "'Vazirmatn', sans-serif";
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

            // Text elements (Block-level and tables: p, li, h1..h6, blockquote, div, th, td, table)
            // Never apply dir=rtl to inline elements (span, a) as it breaks natural BiDi flow of English words
            if (/^(p|li|h1|h2|h3|h4|h5|h6|blockquote|div|th|td|table)$/i.test(tag)) {
                let containsPersian = false;

                // Check text nodes
                for (let child = el.firstChild; child; child = child.nextSibling) {
                    if (child.nodeType === 3) {
                        const text = child.nodeValue;
                        if (text && PERSIAN_REGEX.test(text)) {
                            containsPersian = true;
                            break;
                        }
                    }
                }

                // If tag is p, li, h1..h6, blockquote, th, td, table, check full text if not found in direct children
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
                        el.style.fontFamily = "'Vazirmatn', sans-serif";

                        // If li, also set list to rtl
                        if (tag === 'li' && el.parentElement && /^(ul|ol)$/i.test(el.parentElement.tagName)) {
                            el.parentElement.setAttribute('dir', 'rtl');
                            el.parentElement.classList.add('persian-list');
                            el.parentElement.style.direction = 'rtl';
                            el.parentElement.style.textAlign = 'right';
                        }

                        // If th or td, also set enclosing table to rtl so columns order RTL
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
        } catch (err) {
            // Never allow an individual element to crash the loop
        }
    }

    function scanAll() {
        try {
            injectStyle(document);
            const allElements = document.querySelectorAll('p, li, h1, h2, h3, h4, h5, h6, blockquote, div, th, td, table, textarea, input, [contenteditable="true"], pre, code');
            for (let i = 0; i < allElements.length; i++) {
                processSingleElement(allElements[i]);
            }
        } catch (e) {}
    }

    let isScheduled = false;
    function scheduleScan() {
        if (isScheduled) return;
        isScheduled = true;
        requestAnimationFrame(() => {
            isScheduled = false;
            scanAll();
        });
    }

    // Run on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            scanAll();
        });
    } else {
        scanAll();
    }

    // Robust MutationObserver
    try {
        const obs = new MutationObserver((mutations) => {
            scheduleScan();
        });
        const root = document.body || document.documentElement;
        if (root) {
            obs.observe(root, { childList: true, subtree: true, characterData: true });
        }
    } catch (e) {}

    // Continuous sweep every 600ms (guarantees streaming tokens and new messages are never missed)
    setInterval(() => {
        scanAll();
    }, 600);

    console.log('[PersianFixer v3.0] Active & bulletproof.');
})();