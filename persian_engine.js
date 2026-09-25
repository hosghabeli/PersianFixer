// ==UserScript==
// @name         Persian RTL & Vazirmatn Engine v3
// @description  Bulletproof RTL & Vazirmatn engine with SVG isolation and crash-proof observer
// @version      3.0
// ==/UserScript==

(function () {
    const PERSIAN_REGEX = /[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]/;

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

/* Preserve Code Blocks & Terminal as Clean LTR */
pre, code, kbd, samp, pre *, code *,
.monaco-editor, .monaco-editor *,
.code-block, [data-code-block],
.font-mono, [class*="mono"] {
  direction: ltr !important;
  text-align: left !important;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace !important;
  unicode-bidi: isolate !important;
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

    function processSingleElement(el) {
        try {
            if (!el || !(el instanceof HTMLElement)) return;

            const tag = el.tagName.toLowerCase();

            // Skip code and editor elements
            if (tag === 'pre' || tag === 'code' || tag === 'script' || tag === 'style' || el.closest('pre, code, .monaco-editor')) {
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
            const allElements = document.querySelectorAll('p, li, h1, h2, h3, h4, h5, h6, blockquote, div, th, td, table, textarea, input, [contenteditable="true"]');
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