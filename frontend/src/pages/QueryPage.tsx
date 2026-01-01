import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { useOpenAITTS } from '@/hooks/useOpenAITTS';
import { useSettings } from '@/hooks/useSettings';
import { useSpeechSynthesis } from '@/hooks/useSpeechSynthesis';
import { queryAccounting, getAuthToken } from '@/services/api';

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

function SearchIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.3-4.3" />
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

const EXAMPLE_QUERIES = [
  '這個月花了多少錢？',
  '飲食類別佔比多少？',
  '哪個類別花最多？',
  '今天有記帳嗎？',
  '本月日均支出多少？',
];

type QueryHistory = {
  query: string;
  answer: string;
  timestamp: Date;
};

export default function QueryPage() {
  const [queryText, setQueryText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<QueryHistory[]>([]);

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
      setQueryText(transcript);
    }
  }, [transcript]);

  // Show errors
  useEffect(() => {
    if (sttError) {
      toast.error(`語音辨識錯誤: ${sttError}`);
    }
  }, [sttError]);

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

  const handleQuery = async (text?: string) => {
    const query = text || queryText;
    if (!query.trim()) {
      toast.error('請輸入查詢內容');
      return;
    }

    if (!getAuthToken()) {
      toast.error('請先在設定頁面設定 API Token');
      return;
    }

    // 如果麥克風正在聆聽，先停止它
    if (isListening) {
      stopListening();
    }

    setIsLoading(true);
    try {
      const response = await queryAccounting(query);
      if (response.success) {
        const newHistory: QueryHistory = {
          query: query,
          answer: response.answer,
          timestamp: new Date(),
        };
        setHistory([newHistory, ...history]);
        setQueryText('');
        resetTranscript();

        // Speak the answer
        await speakMessage(response.answer);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '查詢失敗';
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

  const handleExampleClick = (example: string) => {
    setQueryText(example);
  };

  return (
    <div className="space-y-6">
      {/* Query Input */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">帳務查詢</CardTitle>
          <CardDescription>
            用自然語言詢問您的消費狀況
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="例如：這個月花了多少錢？"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !isLoading && handleQuery()}
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
            <Button
              size="icon"
              onClick={() => handleQuery()}
              disabled={isLoading || !queryText.trim()}
            >
              <SearchIcon className="h-4 w-4" />
            </Button>
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

          {/* Example Queries */}
          <div className="space-y-2">
            <div className="text-sm text-muted-foreground">試試這些問題：</div>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_QUERIES.map((example) => (
                <Button
                  key={example}
                  variant="outline"
                  size="sm"
                  onClick={() => handleExampleClick(example)}
                  disabled={isLoading}
                  className="text-xs"
                >
                  {example}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Query History */}
      {history.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">查詢記錄</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {history.map((item, index) => (
              <div key={index} className="border-b last:border-0 pb-4 last:pb-0">
                <div className="text-sm text-muted-foreground mb-1">
                  Q: {item.query}
                </div>
                <div className="text-sm bg-muted rounded-lg p-3 flex items-start gap-2">
                  <div className="flex-1">{item.answer}</div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 shrink-0"
                    onClick={() => speakMessage(item.answer)}
                    disabled={isSpeaking}
                  >
                    <SpeakerIcon className="h-3 w-3" />
                  </Button>
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {item.timestamp.toLocaleTimeString()}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {isLoading && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            <LoadingIcon className="h-6 w-6 animate-spin mx-auto mb-2" />
            正在查詢...
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
              正在播放語音...
            </>
          )}
        </div>
      )}
    </div>
  );
}
