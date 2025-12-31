import { useState, useEffect, useCallback } from 'react';
import type { TTSVoice } from '@/services/api';

export type AppSettings = {
  useNaturalVoice: boolean; // 使用 OpenAI TTS（付費）vs Web Speech API（免費）
  ttsVoice: TTSVoice;
  ttsSpeed: number;
};

const SETTINGS_KEY = 'app_settings';

const defaultSettings: AppSettings = {
  useNaturalVoice: true, // 預設使用自然語音
  ttsVoice: 'nova',
  ttsSpeed: 1.0,
};

export const useSettings = () => {
  const [settings, setSettings] = useState<AppSettings>(() => {
    try {
      const stored = localStorage.getItem(SETTINGS_KEY);
      if (stored) {
        return { ...defaultSettings, ...JSON.parse(stored) };
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
