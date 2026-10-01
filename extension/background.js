// PersianFixer - Background Service Worker (Manifest V3)

const DEFAULT_SETTINGS = {
  enabled: true,
  mode: 'ai_only', // strictly only AI chat platforms
  aiDomains: [
    'chatgpt.com',
    'chat.openai.com',
    'claude.ai',
    'gemini.google.com',
    'aistudio.google.com',
    'chat.deepseek.com',
    'deepseek.com',
    'perplexity.ai',
    'poe.com',
    'copilot.microsoft.com',
    'chat.mistral.ai',
    'groq.com',
    'v0.dev',
    'huggingface.co'
  ],
  blacklist: [],
  forceVazirFont: true,
  smartTables: true,
  fontSizeDelta: 0
};

// Initialize settings on install or update
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.get(DEFAULT_SETTINGS, (stored) => {
    // Ensure mode defaults to ai_only
    const mode = (stored && stored.mode === 'ai_only') ? 'ai_only' : 'ai_only';
    chrome.storage.sync.set({ ...DEFAULT_SETTINGS, ...stored, mode });
  });

  // Context Menu for quick RTL toggle on selected element
  chrome.contextMenus.create({
    id: 'toggle-element-rtl',
    title: 'تغییر جهت متن (RTL / LTR)',
    contexts: ['selection', 'editable', 'page']
  });
});

// Handle Context Menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'toggle-element-rtl' && tab?.id) {
    chrome.tabs.sendMessage(tab.id, { action: 'toggle-selected-rtl' }).catch(() => {});
  }
});

// Handle keyboard shortcut (Alt+Shift+P)
chrome.commands.onCommand.addListener(async (command) => {
  if (command === 'toggle-active') {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id || !tab.url) return;

    try {
      const url = new URL(tab.url);
      const hostname = url.hostname;
      
      chrome.storage.sync.get(DEFAULT_SETTINGS, (settings) => {
        let blacklist = settings.blacklist || [];
        const isBlacklisted = blacklist.includes(hostname);

        if (isBlacklisted) {
          blacklist = blacklist.filter(h => h !== hostname);
        } else {
          blacklist.push(hostname);
        }

        chrome.storage.sync.set({ blacklist }, () => {
          chrome.tabs.sendMessage(tab.id, { 
            action: 'settings-updated', 
            enabledOnThisSite: isBlacklisted 
          }).catch(() => {});
          updateBadge(tab.id, isBlacklisted);
        });
      });
    } catch (e) {
      console.error(e);
    }
  }
});

// Helper to update action badge
function updateBadge(tabId, isActive) {
  if (typeof tabId !== 'number' || tabId < 0) return;
  try {
    if (isActive) {
      chrome.action.setBadgeText({ tabId, text: '' });
    } else {
      chrome.action.setBadgeText({ tabId, text: 'OFF' });
      chrome.action.setBadgeBackgroundColor({ tabId, color: '#e74c3c' });
    }
  } catch (e) {}
}

// Listen to messages from content script or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'check-status') {
    const tabId = sender.tab ? sender.tab.id : null;
    if (typeof tabId === 'number' && tabId >= 0) {
      updateBadge(tabId, message.isActive);
    }
    sendResponse({ success: true });
  }
});
