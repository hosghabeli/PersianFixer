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

  // 2. Load stored settings
  chrome.storage.sync.get({
    enabled: true,
    mode: 'all',
    blacklist: [],
    forceVazirFont: true,
    smartTables: true,
    fontSizeDelta: 0
  }, (settings) => {
    globalToggle.checked = settings.enabled;
    if (settings.mode === 'ai_only') {
      modeAi.checked = true;
    } else {
      modeAll.checked = true;
    }
    optFont.checked = settings.forceVazirFont;
    optTables.checked = settings.smartTables;
    fontScale.value = settings.fontSizeDelta || 0;
    updateFontScaleText(fontScale.value);

    updateSiteButtonState(settings.blacklist || []);
  });

  function updateFontScaleText(val) {
    const percent = 100 + parseInt(val, 10);
    fontScaleValue.textContent = `${percent}٪`;
  }

  function updateSiteButtonState(blacklist) {
    if (!currentHostname) return;
    const isBlacklisted = blacklist.includes(currentHostname);
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
    if (modeAll.checked) saveSettings({ mode: 'all' });
  });

  modeAi.addEventListener('change', () => {
    if (modeAi.checked) saveSettings({ mode: 'ai_only' });
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
