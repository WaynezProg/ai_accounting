import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import ReactMarkdown from 'react-markdown';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { useOpenAITTS } from '@/hooks/useOpenAITTS';
import { useSettings } from '@/hooks/useSettings';
import { useSpeechSynthesis } from '@/hooks/useSpeechSynthesis';
import { pickWebVoice } from '@/utils/tts';
import { queryAccounting, getAuthToken, getQueryHistory } from '@/services/api';
import type { QueryHistoryItem } from '@/services/api';

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

function SendIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="m22 2-7 20-4-9-9-4Z" />
      <path d="M22 2 11 13" />
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

function XIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}

function HistoryIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
      <path d="M3 3v5h5" />
      <path d="M12 7v5l4 2" />
    </svg>
  );
}

const EXAMPLE_QUERIES = [
  '這個月花了多少錢？',
  '最近買了什麼？',
  '跟上個月比如何？',
  '幫我規劃預算',
  '什麼是 ETF？',
];

// 對話氣泡元件
function ChatBubble({
  isUser,
  message,
  timestamp,
  onSpeak,
  isSpeaking,
}: {
  isUser: boolean;
  message: string;
  timestamp: string;
  onSpeak?: () => void;
  isSpeaking?: boolean;
}) {
  const formattedTime = new Date(timestamp).toLocaleString('zh-TW', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[85%] ${isUser ? 'order-1' : 'order-1'}`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-primary text-primary-foreground rounded-br-md'
              : 'bg-muted rounded-bl-md'
          }`}
        >
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap break-words">{message}</p>
          ) : (
            <div className="text-sm prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-headings:my-2 prose-headings:text-base prose-strong:text-inherit">
              <ReactMarkdown>{message}</ReactMarkdown>
            </div>
          )}
        </div>
        <div className={`flex items-center gap-2 mt-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
          <span className="text-xs text-muted-foreground">{formattedTime}</span>
          {!isUser && onSpeak && (
            <Button
              variant="ghost"
              size="icon"
              className="h-5 w-5"
              onClick={onSpeak}
              disabled={isSpeaking}
            >
              <SpeakerIcon className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

// 骨架屏元件
function ChatSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      {[1, 2, 3].map((i) => (
        <div key={i}>
          <div className="flex justify-end mb-4">
            <div className="bg-muted rounded-2xl rounded-br-md h-10 w-48" />
          </div>
          <div className="flex justify-start mb-4">
            <div className="bg-muted rounded-2xl rounded-bl-md h-24 w-64" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function QueryPage() {
  const [queryText, setQueryText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // 歷史記錄狀態
  const [history, setHistory] = useState<QueryHistoryItem[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  
  // 搜尋狀態
  const [searchText, setSearchText] = useState('');
  const [isSearching, setIsSearching] = useState(false);

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
    cancel: webCancel,
    isSpeaking: webIsSpeaking,
    isSupported: webTtsSupported,
    voices: webVoices,
    setVoice: setWebVoice,
  } = useSpeechSynthesis('zh-TW');

  // OpenAI TTS (paid, natural voice)
  const {
    speak: openaiSpeak,
    stop: openaiStop,
    isSpeaking: openaiIsSpeaking,
    isLoading: openaiIsLoading,
    error: openaiError,
    setVoice,
    setSpeed,
  } = useOpenAITTS(settings.ttsVoice);

  const isOpenAIProvider = settings.ttsProvider === 'openai';
  const isSpeaking = isOpenAIProvider ? (openaiIsSpeaking || openaiIsLoading) : webIsSpeaking;
  const isRemoteLoading = isOpenAIProvider ? openaiIsLoading : false;

  // 載入歷史記錄
  const loadHistory = useCallback(async (search?: string, cursor?: string) => {
    if (!getAuthToken()) return;

    try {
      setIsLoadingHistory(true);
      const response = await getQueryHistory({
        limit: 20,
        cursor,
        search: search || undefined,
      });

      if (cursor) {
        // 載入更多 - 去重避免臨時 ID 項目與真實資料庫記錄重複
        setHistory((prev) => {
          const existingQueries = new Set(
            prev.map((item) => `${item.query}|${item.answer}`)
          );
          const newItems = response.items.filter(
            (item) => !existingQueries.has(`${item.query}|${item.answer}`)
          );
          return [...prev, ...newItems];
        });
      } else {
        // 初次載入或搜尋
        setHistory(response.items);
      }
      setNextCursor(response.next_cursor);
      setTotalCount(response.total);
    } catch (error) {
      console.error('Failed to load history:', error);
      // 不顯示錯誤提示，避免干擾使用者
    } finally {
      setIsLoadingHistory(false);
    }
  }, []);

  // 初次載入
  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

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
    if (isOpenAIProvider && openaiError) {
      toast.error(`語音合成錯誤: ${openaiError}`);
    }
  }, [isOpenAIProvider, openaiError]);

  // Sync voice setting
  useEffect(() => {
    setVoice(settings.ttsVoice);
  }, [settings.ttsVoice, setVoice]);

  useEffect(() => {
    setSpeed(settings.ttsSpeed);
  }, [settings.ttsSpeed, setSpeed]);

  useEffect(() => {
    if (!webTtsSupported || !webVoices.length || settings.ttsProvider !== 'web') return;
    const selected = pickWebVoice(webVoices, settings.ttsWebVoice, 'zh-TW');
    if (selected) {
      setWebVoice(selected);
    }
  }, [settings.ttsProvider, settings.ttsWebVoice, webTtsSupported, webVoices, setWebVoice]);

  const speakMessage = async (message: string) => {
    if (isOpenAIProvider) {
      await openaiSpeak(message);
    } else if (webTtsSupported) {
      webSpeak(message);
    } else {
      toast.error('您的瀏覽器不支援語音播放');
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
        // 新增到本地記錄最前面（後端已自動儲存）
        const newItem: QueryHistoryItem = {
          id: Date.now(), // 臨時 ID
          query: query,
          answer: response.answer,
          created_at: new Date().toISOString(),
        };
        setHistory((prev) => [newItem, ...prev]);
        setTotalCount((prev) => prev + 1);
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

  // 搜尋處理
  const handleSearch = () => {
    setIsSearching(!!searchText);
    loadHistory(searchText);
  };

  const handleClearSearch = () => {
    setSearchText('');
    setIsSearching(false);
    loadHistory();
  };

  // 載入更多
  const handleLoadMore = () => {
    if (nextCursor) {
      loadHistory(isSearching ? searchText : undefined, nextCursor);
    }
  };

  return (
    <div className="space-y-4">
      {/* Query Input */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">財務小助手</CardTitle>
          <CardDescription>
            查詢帳務、詢問理財知識，或隨意聊聊
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="問我任何問題..."
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
              <SendIcon className="h-4 w-4" />
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
            <div className="text-sm text-muted-foreground">試試問我：</div>
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

      {/* Loading State */}
      {isLoading && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            <LoadingIcon className="h-6 w-6 animate-spin mx-auto mb-2" />
            正在查詢...
          </CardContent>
        </Card>
      )}

      {/* Query History */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <HistoryIcon className="h-5 w-5 text-muted-foreground" />
              <CardTitle className="text-lg">查詢記錄</CardTitle>
              {totalCount > 0 && (
                <span className="text-sm text-muted-foreground">({totalCount})</span>
              )}
            </div>
          </div>
          {/* 搜尋框 */}
          <div className="flex gap-2 mt-3">
            <div className="relative flex-1">
              <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="搜尋歷史記錄..."
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="pl-9 pr-8"
              />
              {searchText && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-6 w-6"
                  onClick={handleClearSearch}
                >
                  <XIcon className="h-3 w-3" />
                </Button>
              )}
            </div>
            <Button variant="outline" size="icon" onClick={handleSearch}>
              <SearchIcon className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoadingHistory && history.length === 0 ? (
            <ChatSkeleton />
          ) : history.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              {isSearching ? '找不到符合的記錄' : '尚無查詢記錄，試著問我問題吧！'}
            </div>
          ) : (
            <div className="space-y-2">
              {/* 對話氣泡列表 */}
              {history.map((item) => (
                <div key={item.id}>
                  {/* 使用者問題 */}
                  <ChatBubble
                    isUser={true}
                    message={item.query}
                    timestamp={item.created_at}
                  />
                  {/* AI 回答 */}
                  <ChatBubble
                    isUser={false}
                    message={item.answer}
                    timestamp={item.created_at}
                    onSpeak={() => speakMessage(item.answer)}
                    isSpeaking={isSpeaking}
                  />
                </div>
              ))}

              {/* 載入更多按鈕 */}
              {nextCursor && (
                <div className="pt-4 text-center">
                  <Button
                    variant="outline"
                    onClick={handleLoadMore}
                    disabled={isLoadingHistory}
                  >
                    {isLoadingHistory ? (
                      <>
                        <LoadingIcon className="h-4 w-4 animate-spin mr-2" />
                        載入中...
                      </>
                    ) : (
                      '載入更多'
                    )}
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Speaking Indicator */}
      {isSpeaking && (
        <div
          className="fixed bottom-20 right-4 rounded-full bg-primary px-4 py-2 text-sm text-primary-foreground shadow-lg flex items-center gap-2 cursor-pointer"
          onClick={() => {
            if (isOpenAIProvider) {
              openaiStop();
              return;
            }
            webCancel();
          }}
        >
          {isRemoteLoading ? (
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
