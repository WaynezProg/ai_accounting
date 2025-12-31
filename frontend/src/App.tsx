import { useState, useEffect } from 'react';
import { Toaster, toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { useSpeechSynthesis } from '@/hooks/useSpeechSynthesis';
import { createEntry, setAuthToken, getAuthToken } from '@/services/api';
import type { AccountingRecord } from '@/services/api';

function App() {
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastResult, setLastResult] = useState<AccountingRecord | null>(null);
  const [lastFeedback, setLastFeedback] = useState<string | null>(null);
  const [token, setToken] = useState<string>(getAuthToken() || '');

  const {
    transcript,
    isListening,
    isSupported: sttSupported,
    error: sttError,
    startListening,
    stopListening,
    resetTranscript,
  } = useSpeechRecognition('zh-TW');

  const { speak, isSpeaking, isSupported: ttsSupported } = useSpeechSynthesis('zh-TW');

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

  const handleTokenSave = () => {
    setAuthToken(token);
    toast.success('Token 已儲存');
  };

  const handleSubmit = async () => {
    if (!inputText.trim()) {
      toast.error('請輸入記帳內容');
      return;
    }

    if (!getAuthToken()) {
      toast.error('請先設定 API Token');
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
        if (ttsSupported) {
          speak(response.message);
        }

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
    <div className="min-h-screen bg-background p-4 md:p-8">
      <Toaster position="top-center" richColors />

      <div className="mx-auto max-w-md space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">語音記帳助手</h1>
          <p className="text-muted-foreground mt-2">說出或輸入您的消費，AI 自動幫您記帳</p>
        </div>

        {/* Token Settings */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">API Token</CardTitle>
            <CardDescription>輸入您的 API Token 以使用服務</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input
                type="password"
                placeholder="輸入 API Token"
                value={token}
                onChange={(e) => setToken(e.target.value)}
              />
              <Button onClick={handleTokenSave} variant="secondary">
                儲存
              </Button>
            </div>
          </CardContent>
        </Card>

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
          <div className="fixed bottom-4 right-4 rounded-full bg-primary px-4 py-2 text-sm text-primary-foreground shadow-lg">
            正在播放語音回饋...
          </div>
        )}
      </div>
    </div>
  );
}

// Simple icon components
function MicrophoneIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" x2="12" y1="19" y2="22" />
    </svg>
  );
}

function StopIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <rect x="6" y="6" width="12" height="12" rx="2" />
    </svg>
  );
}

export default App;
