import { useState, useCallback, useRef } from 'react';
import { synthesizeSpeech } from '@/services/api';
import type { TTSVoice } from '@/services/api';

export type UseOpenAITTSResult = {
  speak: (text: string) => Promise<void>;
  stop: () => void;
  isSpeaking: boolean;
  isLoading: boolean;
  error: string | null;
  voice: TTSVoice;
  setVoice: (voice: TTSVoice) => void;
  speed: number;
  setSpeed: (speed: number) => void;
};

export const useOpenAITTS = (defaultVoice: TTSVoice = 'nova'): UseOpenAITTSResult => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [voice, setVoice] = useState<TTSVoice>(defaultVoice);
  const [speed, setSpeed] = useState(1.0);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const objectUrlRef = useRef<string | null>(null);

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

  const speak = useCallback(
    async (text: string) => {
      if (!text.trim()) return;

      // Clean up previous audio
      cleanup();
      setError(null);
      setIsLoading(true);

      try {
        // Call OpenAI TTS API
        const audioBlob = await synthesizeSpeech(text, voice, speed);

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
          cleanup();
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
    isSpeaking,
    isLoading,
    error,
    voice,
    setVoice,
    speed,
    setSpeed,
  };
};

export default useOpenAITTS;
