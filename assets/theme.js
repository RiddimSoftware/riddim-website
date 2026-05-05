(() => {
  const storageKey = (window.__riddimTheme && window.__riddimTheme.storageKey) || "riddim-theme";
  const root = document.documentElement;
  const themeColorMetas = {
    light: document.querySelector('meta[name="theme-color"][data-theme-color="light"]'),
    dark: document.querySelector('meta[name="theme-color"][data-theme-color="dark"]')
  };
  const manifestLink = document.querySelector('link[rel="manifest"][data-manifest-light][data-manifest-dark]');
  const media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  const readPreference = () => {
    try {
      const value = window.localStorage.getItem(storageKey);
      return value === 'light' || value === 'dark' || value === 'system' ? value : 'system';
    } catch {
      return 'system';
    }
  };

  const writePreference = (preference) => {
    try {
      if (preference === 'system') {
        window.localStorage.removeItem(storageKey);
        return;
      }
      window.localStorage.setItem(storageKey, preference);
    } catch {
      // Ignore storage failures.
    }
  };

  const systemTheme = () => (media && media.matches ? 'dark' : 'light');

  const setThemeColorMode = (preference, theme) => {
    if (themeColorMetas.light && themeColorMetas.dark) {
      if (preference === 'system') {
        themeColorMetas.light.media = '(prefers-color-scheme: light)';
        themeColorMetas.dark.media = '(prefers-color-scheme: dark)';
      } else if (theme === 'dark') {
        themeColorMetas.light.media = 'not all';
        themeColorMetas.dark.media = 'all';
      } else {
        themeColorMetas.light.media = 'all';
        themeColorMetas.dark.media = 'not all';
      }
    }
  };

  const setManifest = (theme) => {
    if (!manifestLink) {
      return;
    }

    const nextHref = theme === 'dark' ? manifestLink.dataset.manifestDark : manifestLink.dataset.manifestLight;
    if (manifestLink.getAttribute('href') !== nextHref) {
      manifestLink.setAttribute('href', nextHref);
    }
  };

  const updateControls = (preference, theme) => {
    document.querySelectorAll('[data-theme-select]').forEach((control) => {
      control.value = preference;
    });

    const statusText = preference === 'system'
      ? `Following system (${theme})`
      : `Locked to ${theme}`;

    document.querySelectorAll('[data-theme-status]').forEach((status) => {
      status.textContent = statusText;
    });
  };

  const applyTheme = (preference, { persist = false } = {}) => {
    const theme = preference === 'system' ? systemTheme() : preference;

    root.dataset.themeUi = 'ready';
    root.dataset.themePreference = preference;
    root.dataset.theme = theme;
    root.style.colorScheme = theme;

    setThemeColorMode(preference, theme);
    setManifest(theme);
    updateControls(preference, theme);

    if (persist) {
      writePreference(preference);
    }

    window.dispatchEvent(new CustomEvent('riddim-themechange', {
      detail: { preference, theme }
    }));
  };

  const currentPreference = () => root.dataset.themePreference || readPreference();

  document.querySelectorAll('[data-theme-select]').forEach((control) => {
    control.addEventListener('change', (event) => {
      applyTheme(event.target.value, { persist: true });
    });
  });

  const handleSystemChange = () => {
    if (currentPreference() === 'system') {
      applyTheme('system');
    }
  };

  if (media) {
    if (typeof media.addEventListener === 'function') {
      media.addEventListener('change', handleSystemChange);
    } else if (typeof media.addListener === 'function') {
      media.addListener(handleSystemChange);
    }
  }

  applyTheme(currentPreference());
})();
