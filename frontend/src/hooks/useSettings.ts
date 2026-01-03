import { useState, useEffect, useCallback } from 'react';
import type { TTSVoice } from '@/services/api';

export type TTSProvider = 'web' | 'openai';

export type AppSettings = {
  ttsProvider: TTSProvider;
  ttsWebVoice: string; // SpeechSynthesisVoice.voiceURI
  ttsVoice: TTSVoice;
  ttsSpeed: number;
};

const SETTINGS_KEY = 'app_settings';

const defaultSettings: AppSettings = {
  ttsProvider: 'web', // 預設使用免費語音
  ttsWebVoice: '',
  ttsVoice: 'nova',
  ttsSpeed: 1.0,
};

export const useSettings = () => {
  const [settings, setSettings] = useState<AppSettings>(() => {
    try {
      const stored = localStorage.getItem(SETTINGS_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as Partial<AppSettings> & {
          useNaturalVoice?: boolean;
        };
        const storedProvider = parsed.ttsProvider;
        const ttsProvider: TTSProvider =
          storedProvider === 'openai' || storedProvider === 'web'
            ? storedProvider
            : (parsed.useNaturalVoice ? 'openai' : 'web');
        return { ...defaultSettings, ...parsed, ttsProvider };
      }
    } catch {
      // Ignore parse errors
    }
    return defaultSettings;
  });

  // Persist settings to localStorage
  useEffect(() => {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  }, [settings]);

  const updateSettings = useCallback((updates: Partial<AppSettings>) => {
    setSettings((prev) => ({ ...prev, ...updates }));
  }, []);

  const resetSettings = useCallback(() => {
    setSettings(defaultSettings);
  }, []);

  return {
    settings,
    updateSettings,
    resetSettings,
  };
};

export default useSettings;
