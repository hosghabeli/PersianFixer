// PersianFixer - Popup Logic

document.addEventListener('DOMContentLoaded', async () => {
  const globalToggle = document.getElementById('global-toggle');
  const siteDomainEl = document.getElementById('site-domain');
  const siteToggleBtn = document.getElementById('site-toggle-btn');
  const siteCard = document.getElementById('site-card');
  const modeAll = document.getElementById('mode-all');
  const modeAi = document.getElementById('mode-ai');
  const optFont = document.getElementById('opt-font');
  const optTables = document.getElementById('opt-tables');
  const fontScale = document.getElementById('font-scale');
  const fontScaleValue = document.getElementById('font-scale-value');

  let currentHostname = '';
  let activeTabId = null;

  // 1. Get active tab information
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url && (tab.url.startsWith('http://') || tab.url.startsWith('https://'))) {
      const url = new URL(tab.url);
      currentHostname = url.hostname;
      siteDomainEl.textContent = currentHostname;
      activeTabId = tab.id;
    } else {
      siteDomainEl.textContent = 'صفحه سیستمی یا داخلی';
      siteToggleBtn.style.display = 'none';
    }
  } catch (e) {
    siteDomainEl.textContent = 'عدم دسترسی به تب';
    siteToggleBtn.style.display = 'none';
  }

  const AI_DOMAINS = [
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

  // 2. Load stored settings
  chrome.storage.sync.get({
    enabled: true,
    mode: 'ai_only',
    blacklist: [],
    forceVazirFont: true,
    smartTables: true,
    fontSizeDelta: 0
  }, (settings) => {
    globalToggle.checked = settings.enabled;
    const mode = settings.mode || 'ai_only';
    if (mode === 'all') {
      modeAll.checked = true;
    } else {
      modeAi.checked = true;
    }
    optFont.checked = settings.forceVazirFont;
    optTables.checked = settings.smartTables;
    fontScale.value = settings.fontSizeDelta || 0;
    updateFontScaleText(fontScale.value);

    updateSiteButtonState(settings.blacklist || [], mode);
  });

  function updateFontScaleText(val) {
    const percent = 100 + parseInt(val, 10);
    fontScaleValue.textContent = `${percent}٪`;
  }

  function updateSiteButtonState(blacklist, currentMode) {
    if (!currentHostname) return;
    const isAi = AI_DOMAINS.some(d => currentHostname.includes(d));
    const mode = currentMode || (modeAll.checked ? 'all' : 'ai_only');
    const isBlacklisted = blacklist.includes(currentHostname);

    if (mode === 'ai_only' && !isAi) {
      siteToggleBtn.textContent = 'غیرفعال (مخصوص چت‌بات‌های AI)';
      siteToggleBtn.classList.add('disabled-state');
      siteToggleBtn.disabled = true;
      siteToggleBtn.style.opacity = '0.6';
      return;
    }

    siteToggleBtn.disabled = false;
    siteToggleBtn.style.opacity = '1';
    if (isBlacklisted) {
      siteToggleBtn.textContent = 'فعال کردن در این سایت';
      siteToggleBtn.classList.add('disabled-state');
    } else {
      siteToggleBtn.textContent = 'غیرفعال کردن در این سایت';
      siteToggleBtn.classList.remove('disabled-state');
    }
  }

  function notifyTab() {
    if (activeTabId) {
      chrome.tabs.sendMessage(activeTabId, { action: 'settings-updated' }).catch(() => {});
    }
  }

  function saveSettings(partial) {
    chrome.storage.sync.set(partial, () => {
      notifyTab();
    });
  }

  // Event Listeners
  globalToggle.addEventListener('change', () => {
    saveSettings({ enabled: globalToggle.checked });
  });

  modeAll.addEventListener('change', () => {
    if (modeAll.checked) {
      saveSettings({ mode: 'all' });
      chrome.storage.sync.get({ blacklist: [] }, (res) => updateSiteButtonState(res.blacklist, 'all'));
    }
  });

  modeAi.addEventListener('change', () => {
    if (modeAi.checked) {
      saveSettings({ mode: 'ai_only' });
      chrome.storage.sync.get({ blacklist: [] }, (res) => updateSiteButtonState(res.blacklist, 'ai_only'));
    }
  });

  optFont.addEventListener('change', () => {
    saveSettings({ forceVazirFont: optFont.checked });
  });

  optTables.addEventListener('change', () => {
    saveSettings({ smartTables: optTables.checked });
  });

  fontScale.addEventListener('input', () => {
    updateFontScaleText(fontScale.value);
    saveSettings({ fontSizeDelta: parseInt(fontScale.value, 10) });
  });

  siteToggleBtn.addEventListener('click', () => {
    if (!currentHostname) return;
    chrome.storage.sync.get({ blacklist: [] }, (res) => {
      let blacklist = res.blacklist || [];
      if (blacklist.includes(currentHostname)) {
        blacklist = blacklist.filter(h => h !== currentHostname);
      } else {
        blacklist.push(currentHostname);
      }
      chrome.storage.sync.set({ blacklist }, () => {
        updateSiteButtonState(blacklist);
        notifyTab();
      });
    });
  });
});
