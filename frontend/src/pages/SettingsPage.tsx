import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useSettings } from '@/hooks/useSettings';
import { setAuthToken, getAuthToken, generateNewToken, verifyToken } from '@/services/api';
import type { TTSVoice } from '@/services/api';

function CopyIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
      <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
    </svg>
  );
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function RefreshIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
      <path d="M3 3v5h5" />
      <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
      <path d="M16 16h5v5" />
    </svg>
  );
}

const VOICE_OPTIONS: { id: TTSVoice; name: string; description: string }[] = [
  { id: 'nova', name: 'Nova', description: '女性，自然溫柔' },
  { id: 'shimmer', name: 'Shimmer', description: '女性，明亮活潑' },
  { id: 'alloy', name: 'Alloy', description: '中性，平衡自然' },
  { id: 'echo', name: 'Echo', description: '男性，清晰明確' },
  { id: 'fable', name: 'Fable', description: '男性，故事感' },
  { id: 'onyx', name: 'Onyx', description: '男性，沉穩低沉' },
];

export default function SettingsPage() {
  const [token, setToken] = useState<string>(getAuthToken() || '');
  const [isVerifying, setIsVerifying] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [tokenValid, setTokenValid] = useState<boolean | null>(null);
  const [copied, setCopied] = useState(false);

  const { settings, updateSettings, resetSettings } = useSettings();

  // 驗證現有 Token
  useEffect(() => {
    const checkToken = async () => {
      if (!token) {
        setTokenValid(null);
        return;
      }

      setIsVerifying(true);
      try {
        const result = await verifyToken();
        setTokenValid(result.success);
      } catch {
        setTokenValid(false);
      } finally {
        setIsVerifying(false);
      }
    };

    checkToken();
  }, [token]);

  const handleSaveToken = () => {
    setAuthToken(token);
    toast.success('Token 已儲存');
  };

  const handleGenerateToken = async () => {
    setIsGenerating(true);
    try {
      const response = await generateNewToken('Web App Token');
      if (response.success) {
        const newToken = response.token.token;
        setToken(newToken);
        setAuthToken(newToken);
        toast.success('已產生新 Token');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '產生 Token 失敗';
      toast.error(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopyToken = async () => {
    if (!token) return;

    try {
      await navigator.clipboard.writeText(token);
      setCopied(true);
      toast.success('Token 已複製到剪貼簿');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error('複製失敗');
    }
  };

  const maskToken = (t: string): string => {
    if (!t || t.length < 12) return t;
    return t.substring(0, 8) + '...' + t.substring(t.length - 4);
  };

  return (
    <div className="space-y-6">
      {/* Token Management */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">API Token 管理</CardTitle>
          <CardDescription>
            管理您的 API Token，用於網頁版和 Siri 捷徑
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Token Input */}
          <div className="space-y-2">
            <Label htmlFor="token">API Token</Label>
            <div className="flex gap-2">
              <Input
                id="token"
                type="password"
                placeholder="輸入您的 API Token"
                value={token}
                onChange={(e) => setToken(e.target.value)}
              />
              <Button variant="secondary" onClick={handleSaveToken}>
                儲存
              </Button>
            </div>
          </div>

          {/* Token Status */}
          {token && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">狀態：</span>
              {isVerifying ? (
                <span className="text-muted-foreground">驗證中...</span>
              ) : tokenValid === true ? (
                <span className="text-green-600 flex items-center gap-1">
                  <CheckIcon className="h-4 w-4" /> 有效
                </span>
              ) : tokenValid === false ? (
                <span className="text-red-600">無效或已過期</span>
              ) : null}
            </div>
          )}

          {/* Token Display (masked) */}
          {token && (
            <div className="flex items-center gap-2 bg-muted rounded-lg p-3">
              <code className="flex-1 text-sm">{maskToken(token)}</code>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleCopyToken}
                className="h-8 w-8"
              >
                {copied ? (
                  <CheckIcon className="h-4 w-4 text-green-600" />
                ) : (
                  <CopyIcon className="h-4 w-4" />
                )}
              </Button>
            </div>
          )}

          {/* Generate New Token */}
          <div className="pt-2 border-t">
            <Button
              variant="outline"
              onClick={handleGenerateToken}
              disabled={isGenerating}
              className="w-full"
            >
              {isGenerating ? (
                <>
                  <RefreshIcon className="h-4 w-4 mr-2 animate-spin" />
                  產生中...
                </>
              ) : (
                <>
                  <RefreshIcon className="h-4 w-4 mr-2" />
                  產生新 Token
                </>
              )}
            </Button>
            <p className="text-xs text-muted-foreground mt-2">
              產生新 Token 後，請更新 Siri 捷徑中的 Token 設定
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Voice Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">語音設定</CardTitle>
          <CardDescription>
            設定語音輸出的偏好
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Natural Voice Toggle */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="natural-voice">自然語音</Label>
              <p className="text-xs text-muted-foreground">
                使用 AI 自然語音（需消耗 API 額度，約 $0.015/千字）
              </p>
            </div>
            <Switch
              id="natural-voice"
              checked={settings.useNaturalVoice}
              onCheckedChange={(checked) => updateSettings({ useNaturalVoice: checked })}
            />
          </div>

          {/* Voice Selection */}
          {settings.useNaturalVoice && (
            <div className="space-y-3">
              <Label>語音選擇</Label>
              <div className="grid grid-cols-2 gap-2">
                {VOICE_OPTIONS.map((voice) => (
                  <Button
                    key={voice.id}
                    variant={settings.ttsVoice === voice.id ? 'default' : 'outline'}
                    onClick={() => updateSettings({ ttsVoice: voice.id })}
                    className="h-auto py-2 px-3 flex-col items-start"
                  >
                    <span className="font-medium">{voice.name}</span>
                    <span className="text-xs opacity-70">{voice.description}</span>
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Speed Setting */}
          {settings.useNaturalVoice && (
            <div className="space-y-2">
              <Label>語速：{settings.ttsSpeed.toFixed(1)}x</Label>
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={settings.ttsSpeed}
                onChange={(e) => updateSettings({ ttsSpeed: parseFloat(e.target.value) })}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>慢 (0.5x)</span>
                <span>正常 (1.0x)</span>
                <span>快 (2.0x)</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Siri Integration Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Siri 捷徑設定</CardTitle>
          <CardDescription>
            使用 Siri 進行語音記帳
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            1. 在 iPhone 上開啟「捷徑」App
          </p>
          <p className="text-sm text-muted-foreground">
            2. 建立新捷徑，使用「取得 URL 內容」動作
          </p>
          <p className="text-sm text-muted-foreground">
            3. 設定 API 端點和 Bearer Token
          </p>
          <p className="text-sm text-muted-foreground">
            4. 設定觸發語：如「嘿 Siri，我要記帳」
          </p>
          <div className="pt-2 border-t">
            <p className="text-xs text-muted-foreground">
              詳細說明請參考專案文件中的 Siri 捷徑設定教學
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Reset Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">重設設定</CardTitle>
        </CardHeader>
        <CardContent>
          <Button
            variant="outline"
            onClick={() => {
              resetSettings();
              toast.success('設定已重設');
            }}
          >
            重設為預設值
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
