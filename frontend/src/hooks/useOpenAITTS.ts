import { useState, useCallback, useRef } from 'react';
import { synthesizeSpeech } from '@/services/api';
import type { TTSVoice } from '@/services/api';

// 產生快取 key
const getCacheKey = (text: string, voice: TTSVoice, speed: number) => {
  return `${text}|${voice}|${speed}`;
};

export type UseOpenAITTSResult = {
  speak: (text: string) => Promise<void>;
  stop: () => void;
  preload: (text: string) => Promise<void>;
  isSpeaking: boolean;
  isLoading: boolean;
  error: string | null;
  voice: TTSVoice;
  setVoice: (voice: TTSVoice) => void;
  speed: number;
  setSpeed: (speed: number) => void;
  isCached: (text: string) => boolean;
};

export const useOpenAITTS = (defaultVoice: TTSVoice = 'nova'): UseOpenAITTSResult => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [voice, setVoice] = useState<TTSVoice>(defaultVoice);
  const [speed, setSpeed] = useState(1.0);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const objectUrlRef = useRef<string | null>(null);

  // 快取：儲存已合成的音訊 Blob
  const cacheRef = useRef<Map<string, Blob>>(new Map());

  const cleanup = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
  }, []);

  // 檢查是否已快取
  const isCached = useCallback((text: string) => {
    const key = getCacheKey(text, voice, speed);
    return cacheRef.current.has(key);
  }, [voice, speed]);

  // 預載音訊（不播放）
  const preload = useCallback(
    async (text: string) => {
      if (!text.trim()) return;

      const key = getCacheKey(text, voice, speed);

      // 如果已快取，跳過
      if (cacheRef.current.has(key)) return;

      try {
        const audioBlob = await synthesizeSpeech(text, voice, speed);
        cacheRef.current.set(key, audioBlob);
      } catch (err) {
        // 預載失敗不顯示錯誤，播放時再處理
        console.warn('TTS preload failed:', err);
      }
    },
    [voice, speed]
  );

  const speak = useCallback(
    async (text: string) => {
      if (!text.trim()) return;

      // Clean up previous audio
      cleanup();
      setError(null);

      const key = getCacheKey(text, voice, speed);
      let audioBlob: Blob;

      try {
        // 檢查快取
        if (cacheRef.current.has(key)) {
          audioBlob = cacheRef.current.get(key)!;
        } else {
          // 需要呼叫 API
          setIsLoading(true);
          audioBlob = await synthesizeSpeech(text, voice, speed);
          // 存入快取
          cacheRef.current.set(key, audioBlob);
        }

        // Create audio element and play
        const audioUrl = URL.createObjectURL(audioBlob);
        objectUrlRef.current = audioUrl;

        const audio = new Audio(audioUrl);
        audioRef.current = audio;

        audio.onplay = () => {
          setIsSpeaking(true);
          setIsLoading(false);
        };

        audio.onended = () => {
          setIsSpeaking(false);
          // 不清理 objectUrl，讓下次播放可以更快（但會佔用記憶體）
          // 如果想節省記憶體可以取消註解下行
          // cleanup();
        };

        audio.onerror = () => {
          setError('音訊播放失敗');
          setIsSpeaking(false);
          setIsLoading(false);
          cleanup();
        };

        await audio.play();
      } catch (err) {
        const message = err instanceof Error ? err.message : '語音合成失敗';
        setError(message);
        setIsLoading(false);
        setIsSpeaking(false);
      }
    },
    [voice, speed, cleanup]
  );

  const stop = useCallback(() => {
    cleanup();
    setIsSpeaking(false);
    setIsLoading(false);
  }, [cleanup]);

  return {
    speak,
    stop,
    preload,
    isSpeaking,
    isLoading,
    error,
    voice,
    setVoice,
    speed,
    setSpeed,
    isCached,
  };
};

export default useOpenAITTS;
