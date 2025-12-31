import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { useSpeechSynthesis } from '@/hooks/useSpeechSynthesis';
import { useOpenAITTS } from '@/hooks/useOpenAITTS';
import { useSettings } from '@/hooks/useSettings';
import { createEntry, getAuthToken } from '@/services/api';
import type { AccountingRecord } from '@/services/api';

// Icon components
function MicrophoneIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" x2="12" y1="19" y2="22" />
    </svg>
  );
}

function StopIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className}>
      <rect x="6" y="6" width="12" height="12" rx="2" />
    </svg>
  );
}

function SpeakerIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
      <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
      <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
    </svg>
  );
}

function LoadingIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M21 12a9 9 0 1 1-6.219-8.56" />
    </svg>
  );
}

export default function HomePage() {
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastResult, setLastResult] = useState<AccountingRecord | null>(null);
  const [lastFeedback, setLastFeedback] = useState<string | null>(null);

  const { settings } = useSettings();

  const {
    transcript,
    isListening,
    isSupported: sttSupported,
    error: sttError,
    startListening,
    stopListening,
    resetTranscript,
  } = useSpeechRecognition('zh-TW');

  // Web Speech API TTS (free)
  const {
    speak: webSpeak,
    isSpeaking: webIsSpeaking,
    isSupported: webTtsSupported,
  } = useSpeechSynthesis('zh-TW');

  // OpenAI TTS (paid, natural voice)
  const {
    speak: openaiSpeak,
    stop: openaiStop,
    isSpeaking: openaiIsSpeaking,
    isLoading: openaiIsLoading,
    error: openaiError,
    setVoice,
  } = useOpenAITTS(settings.ttsVoice);

  const isSpeaking = settings.useNaturalVoice ? (openaiIsSpeaking || openaiIsLoading) : webIsSpeaking;

  // Update input when transcript changes
  useEffect(() => {
    if (transcript) {
      setInputText(transcript);
    }
  }, [transcript]);

  // Show STT errors
  useEffect(() => {
    if (sttError) {
      toast.error(`語音辨識錯誤: ${sttError}`);
    }
  }, [sttError]);

  // Show OpenAI TTS errors
  useEffect(() => {
    if (openaiError) {
      toast.error(`語音合成錯誤: ${openaiError}`);
    }
  }, [openaiError]);

  // Sync voice setting
  useEffect(() => {
    setVoice(settings.ttsVoice);
  }, [settings.ttsVoice, setVoice]);

  const speakMessage = async (message: string) => {
    if (settings.useNaturalVoice) {
      await openaiSpeak(message);
    } else if (webTtsSupported) {
      webSpeak(message);
    }
  };

  const handleSubmit = async () => {
    if (!inputText.trim()) {
      toast.error('請輸入記帳內容');
      return;
    }

    if (!getAuthToken()) {
      toast.error('請先在設定頁面設定 API Token');
      return;
    }

    setIsLoading(true);
    try {
      const response = await createEntry(inputText);
      if (response.success) {
        setLastResult(response.record);
        setLastFeedback(response.feedback);
        toast.success(response.message);

        // Speak the result
        await speakMessage(response.message);

        // Clear input
        setInputText('');
        resetTranscript();
      } else {
        toast.error(response.message);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '記帳失敗';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceInput = () => {
    if (isListening) {
      stopListening();
    } else {
      resetTranscript();
      startListening();
    }
  };

  return (
    <div className="space-y-6">
      {/* Voice Input */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">記帳輸入</CardTitle>
          <CardDescription>
            {sttSupported ? '點擊麥克風按鈕開始語音輸入，或直接打字' : '您的瀏覽器不支援語音辨識，請直接打字輸入'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="例如：今天午餐吃了85元的便當"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleSubmit()}
              disabled={isLoading}
            />
            {sttSupported && (
              <Button
                variant={isListening ? 'destructive' : 'outline'}
                size="icon"
                onClick={handleVoiceInput}
                disabled={isLoading}
              >
                {isListening ? (
                  <StopIcon className="h-4 w-4" />
                ) : (
                  <MicrophoneIcon className="h-4 w-4" />
                )}
              </Button>
            )}
          </div>

          {isListening && (
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <span className="relative flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex h-3 w-3 rounded-full bg-red-500"></span>
              </span>
              正在聆聽...
            </div>
          )}

          <Button
            className="w-full"
            onClick={handleSubmit}
            disabled={isLoading || !inputText.trim()}
          >
            {isLoading ? '處理中...' : '記帳'}
          </Button>
        </CardContent>
      </Card>

      {/* Result Display */}
      {lastResult && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">最新記帳結果</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-muted-foreground">時間</div>
              <div>{lastResult.時間}</div>
              <div className="text-muted-foreground">類別</div>
              <div>{lastResult.類別}</div>
              <div className="text-muted-foreground">項目</div>
              <div>{lastResult.名稱}</div>
              <div className="text-muted-foreground">金額</div>
              <div className="font-semibold text-primary">{lastResult.花費} {lastResult.幣別}</div>
              {lastResult.支付方式 && (
                <>
                  <div className="text-muted-foreground">付款方式</div>
                  <div>{lastResult.支付方式}</div>
                </>
              )}
            </div>
            {lastFeedback && (
              <div className="mt-4 rounded-lg bg-muted p-3 text-sm">
                <div className="font-medium mb-1">理財回饋</div>
                <div className="text-muted-foreground">{lastFeedback}</div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Speaking Indicator */}
      {isSpeaking && (
        <div
          className="fixed bottom-20 right-4 rounded-full bg-primary px-4 py-2 text-sm text-primary-foreground shadow-lg flex items-center gap-2 cursor-pointer"
          onClick={() => settings.useNaturalVoice && openaiStop()}
        >
          {openaiIsLoading ? (
            <>
              <LoadingIcon className="h-4 w-4 animate-spin" />
              正在生成語音...
            </>
          ) : (
            <>
              <SpeakerIcon className="h-4 w-4" />
              正在播放{settings.useNaturalVoice ? ' AI ' : ''}語音...
            </>
          )}
        </div>
      )}
    </div>
  );
}
