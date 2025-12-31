import { useState, useCallback, useEffect, useRef } from 'react';

export interface UseSpeechSynthesisResult {
  speak: (text: string) => void;
  cancel: () => void;
  isSpeaking: boolean;
  isSupported: boolean;
  voices: SpeechSynthesisVoice[];
  setVoice: (voice: SpeechSynthesisVoice) => void;
  setRate: (rate: number) => void;
  setPitch: (pitch: number) => void;
  selectedVoice: SpeechSynthesisVoice | null;
}

export const useSpeechSynthesis = (lang: string = 'zh-TW'): UseSpeechSynthesisResult => {
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  const rateRef = useRef<number>(1);
  const pitchRef = useRef<number>(1);

  const isSupported = typeof window !== 'undefined' && !!window.speechSynthesis;

  // Load voices
  useEffect(() => {
    if (!isSupported) return;

    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);

      // Auto-select a voice for the specified language
      if (!selectedVoice) {
        const langVoice = availableVoices.find((v) => v.lang.startsWith(lang.split('-')[0]));
        if (langVoice) {
          setSelectedVoice(langVoice);
        }
      }
    };

    loadVoices();

    // Chrome requires this event listener
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    return () => {
      window.speechSynthesis.cancel();
    };
  }, [isSupported, lang, selectedVoice]);

  const speak = useCallback(
    (text: string) => {
      if (!isSupported || !text) return;

      // Cancel any ongoing speech
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = rateRef.current;
      utterance.pitch = pitchRef.current;

      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }

      utterance.onstart = () => {
        setIsSpeaking(true);
      };

      utterance.onend = () => {
        setIsSpeaking(false);
      };

      utterance.onerror = () => {
        setIsSpeaking(false);
      };

      window.speechSynthesis.speak(utterance);
    },
    [isSupported, selectedVoice]
  );

  const cancel = useCallback(() => {
    if (!isSupported) return;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, [isSupported]);

  const setVoice = useCallback((voice: SpeechSynthesisVoice) => {
    setSelectedVoice(voice);
  }, []);

  const setRate = useCallback((rate: number) => {
    rateRef.current = Math.max(0.1, Math.min(10, rate));
  }, []);

  const setPitch = useCallback((pitch: number) => {
    pitchRef.current = Math.max(0, Math.min(2, pitch));
  }, []);

  return {
    speak,
    cancel,
    isSpeaking,
    isSupported,
    voices,
    setVoice,
    setRate,
    setPitch,
    selectedVoice,
  };
};

export default useSpeechSynthesis;
