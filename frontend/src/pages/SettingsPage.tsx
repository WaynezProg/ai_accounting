import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useSettings } from '@/hooks/useSettings';
import { useAuth } from '@/contexts/AuthContext';
import {
  setAuthToken,
  getAuthToken,
  generateNewToken,
  verifyToken,
  getGoogleLoginUrl,
  getMySheet,
  createSheet,
  linkSheet,
  listDriveSheets,
  selectSheet,
  listAPITokens,
  revokeAPIToken,
} from '@/services/api';
import type { TTSVoice, SheetInfo, APITokenInfo, DriveSheetItem } from '@/services/api';

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

function TrashIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M3 6h18" />
      <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
      <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
    </svg>
  );
}

function ExternalLinkIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" x2="21" y1="14" y2="3" />
    </svg>
  );
}

const VOICE_OPTIONS: { id: TTSVoice; name: string; description: string }[] = [
  { id: 'nova', name: 'Nova', description: '女性，推薦中文' },
  { id: 'coral', name: 'Coral', description: '女性，清晰' },
  { id: 'shimmer', name: 'Shimmer', description: '女性，明亮活潑' },
  { id: 'alloy', name: 'Alloy', description: '中性，平衡自然' },
  { id: 'sage', name: 'Sage', description: '中性，穩重' },
  { id: 'echo', name: 'Echo', description: '男性，清晰明確' },
  { id: 'onyx', name: 'Onyx', description: '男性，沉穩低沉' },
  { id: 'ash', name: 'Ash', description: '中性，沉穩' },
];

export default function SettingsPage() {
  const { user, isAuthenticated, authType, logout: authLogout, isLoading: authLoading } = useAuth();
  const [token, setToken] = useState<string>(getAuthToken() || '');
  const [isVerifying, setIsVerifying] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [tokenValid, setTokenValid] = useState<boolean | null>(null);
  const [copied, setCopied] = useState(false);

  // Sheet state
  const [sheetInfo, setSheetInfo] = useState<SheetInfo | null>(null);
  const [isLoadingSheet, setIsLoadingSheet] = useState(false);
  const [isCreatingSheet, setIsCreatingSheet] = useState(false);
  const [sheetUrlInput, setSheetUrlInput] = useState('');
  const [isLinkingSheet, setIsLinkingSheet] = useState(false);

  // Drive sheets list state
  const [driveSheets, setDriveSheets] = useState<DriveSheetItem[]>([]);
  const [isLoadingDriveSheets, setIsLoadingDriveSheets] = useState(false);
  const [showSheetSelector, setShowSheetSelector] = useState(false);
  const [isSelectingSheet, setIsSelectingSheet] = useState(false);

  // API Tokens state
  const [apiTokens, setApiTokens] = useState<APITokenInfo[]>([]);
  const [isLoadingTokens, setIsLoadingTokens] = useState(false);

  const { settings, updateSettings, resetSettings } = useSettings();

  // 載入用戶的 Sheet 資訊
  useEffect(() => {
    if (isAuthenticated && authType === 'oauth') {
      loadSheetInfo();
      loadApiTokens();
    }
  }, [isAuthenticated, authType]);

  const loadSheetInfo = async () => {
    setIsLoadingSheet(true);
    try {
      const response = await getMySheet();
      setSheetInfo(response.sheet);
    } catch (error) {
      console.error('Failed to load sheet info:', error);
    } finally {
      setIsLoadingSheet(false);
    }
  };

  const loadApiTokens = async () => {
    setIsLoadingTokens(true);
    try {
      const response = await listAPITokens();
      setApiTokens(response.tokens);
    } catch (error) {
      console.error('Failed to load API tokens:', error);
    } finally {
      setIsLoadingTokens(false);
    }
  };

  const handleCreateSheet = async () => {
    setIsCreatingSheet(true);
    try {
      const response = await createSheet();
      if (response.success && response.sheet) {
        setSheetInfo(response.sheet);
        toast.success('Google Sheet 建立成功！');
      }
    } catch (error) {
      toast.error('建立 Sheet 失敗');
    } finally {
      setIsCreatingSheet(false);
    }
  };

  const handleLinkSheet = async () => {
    if (!sheetUrlInput.trim()) {
      toast.error('請輸入 Google Sheet URL');
      return;
    }
    setIsLinkingSheet(true);
    try {
      const response = await linkSheet(sheetUrlInput.trim());
      if (response.success && response.sheet) {
        setSheetInfo(response.sheet);
        setSheetUrlInput('');
        toast.success('Google Sheet 連結成功！');
      }
    } catch (error) {
      toast.error('連結 Sheet 失敗，請確認 URL 正確且有存取權限');
    } finally {
      setIsLinkingSheet(false);
    }
  };

  const handleChangeSheet = () => {
    setSheetInfo(null);
    setShowSheetSelector(false);
  };

  const loadDriveSheets = async () => {
    console.log('loadDriveSheets called');
    setIsLoadingDriveSheets(true);
    try {
      const response = await listDriveSheets();
      console.log('Drive sheets loaded:', response.sheets);
      console.log('Number of sheets:', response.sheets.length);
      setDriveSheets(response.sheets);
      setShowSheetSelector(true);
      console.log('showSheetSelector set to true');
    } catch (error) {
      console.error('Load drive sheets error:', error);
      toast.error('載入 Google Sheets 列表失敗');
    } finally {
      setIsLoadingDriveSheets(false);
    }
  };

  const handleSelectSheet = async (sheet: DriveSheetItem) => {
    console.log('handleSelectSheet called with:', sheet);
    setIsSelectingSheet(true);
    try {
      console.log('Calling selectSheet API with id:', sheet.id, 'name:', sheet.name);
      const response = await selectSheet(sheet.id, sheet.name);
      console.log('selectSheet API response:', response);
      if (response.success && response.sheet) {
        setSheetInfo(response.sheet);
        setShowSheetSelector(false);
        toast.success(`已選擇 "${sheet.name}"`);
      } else {
        toast.error(response.message || '選擇 Sheet 失敗');
      }
    } catch (error) {
      console.error('Select sheet error:', error);
      const errorMessage = error instanceof Error ? error.message : '選擇 Sheet 失敗';
      toast.error(errorMessage);
    } finally {
      setIsSelectingSheet(false);
    }
  };

  const handleRevokeToken = async (tokenId: number) => {
    try {
      await revokeAPIToken(tokenId);
      setApiTokens(apiTokens.filter(t => t.id !== tokenId));
      toast.success('Token 已撤銷');
    } catch (error) {
      toast.error('撤銷 Token 失敗');
    }
  };

  // 驗證現有 Token（僅在非 OAuth 登入時）
  useEffect(() => {
    if (authType === 'oauth') return; // OAuth 用戶不需要驗證 API Token

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
  }, [token, authType]);

  const handleSaveToken = () => {
    setAuthToken(token);
    toast.success('Token 已儲存');
  };

  const handleGenerateToken = async () => {
    setIsGenerating(true);
    try {
      const response = await generateNewToken('Web App Token');
      if (response.success) {
        const newToken = response.token;
        setToken(newToken);
        setAuthToken(newToken);
        toast.success('已產生新 Token');
        // 重新載入 Token 列表
        if (isAuthenticated && authType === 'oauth') {
          loadApiTokens();
        }
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

  const handleGoogleLogin = () => {
    window.location.href = getGoogleLoginUrl();
  };

  const handleLogout = async () => {
    await authLogout();
    setToken('');
    setTokenValid(null);
    setSheetInfo(null);
    setApiTokens([]);
    toast.success('已登出');
  };

  return (
    <div className="space-y-6">
      {/* Account Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">帳戶</CardTitle>
          <CardDescription>
            {isAuthenticated ? '管理您的帳戶設定' : '登入以使用完整功能'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {authLoading ? (
            <div className="text-center text-muted-foreground">載入中...</div>
          ) : isAuthenticated && user ? (
            <div className="space-y-4">
              {/* User Info */}
              <div className="flex items-center gap-4">
                {user.picture && (
                  <img
                    src={user.picture}
                    alt={user.name}
                    className="w-12 h-12 rounded-full"
                  />
                )}
                <div>
                  <p className="font-medium">{user.name}</p>
                  <p className="text-sm text-muted-foreground">{user.email}</p>
                </div>
              </div>
              <Button variant="outline" onClick={handleLogout}>
                登出
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                使用 Google 帳號登入，可以建立專屬的記帳 Sheet
              </p>
              <Button onClick={handleGoogleLogin} className="w-full">
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                使用 Google 帳號登入
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Google Sheet Management (OAuth users only) */}
      {isAuthenticated && authType === 'oauth' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Google Sheet</CardTitle>
            <CardDescription>
              您的專屬記帳試算表
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoadingSheet ? (
              <div className="text-center text-muted-foreground">載入中...</div>
            ) : sheetInfo ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between bg-muted rounded-lg p-3">
                  <div>
                    <p className="font-medium">{sheetInfo.sheet_name}</p>
                    <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                      {sheetInfo.sheet_id}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => window.open(sheetInfo.sheet_url, '_blank')}
                  >
                    <ExternalLinkIcon className="h-4 w-4 mr-1" />
                    開啟
                  </Button>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleChangeSheet}
                  className="w-full"
                >
                  更換 Sheet
                </Button>
              </div>
            ) : showSheetSelector ? (
              /* Sheet 選擇列表 */
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium">從 Google Drive 選擇</p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowSheetSelector(false)}
                  >
                    返回
                  </Button>
                </div>

                {isLoadingDriveSheets ? (
                  <div className="text-center text-muted-foreground py-4">載入中...</div>
                ) : driveSheets.length === 0 ? (
                  <div className="text-center text-muted-foreground py-4">
                    找不到任何 Google Sheets
                  </div>
                ) : (
                  <div className="space-y-2">
                    <p className="text-xs text-muted-foreground">
                      找到 {driveSheets.length} 個 Sheets（點擊選擇）
                    </p>
                    {isSelectingSheet && (
                      <div className="text-center text-muted-foreground py-2">
                        選擇中...
                      </div>
                    )}
                    <div className="max-h-[300px] overflow-y-auto space-y-2">
                      {driveSheets.map((sheet, index) => {
                        console.log(`Rendering sheet ${index}:`, sheet.id, sheet.name);
                        return (
                          <div
                            key={sheet.id}
                            role="button"
                            tabIndex={0}
                            onClick={() => {
                              console.log('Sheet item clicked:', sheet.id, sheet.name);
                              handleSelectSheet(sheet);
                            }}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' || e.key === ' ') {
                                handleSelectSheet(sheet);
                              }
                            }}
                            className={`w-full text-left p-3 rounded-lg border cursor-pointer transition-colors hover:bg-accent hover:text-accent-foreground ${isSelectingSheet ? 'opacity-50 pointer-events-none' : ''}`}
                          >
                            <p className="font-medium truncate">{sheet.name}</p>
                            <p className="text-xs text-muted-foreground">
                              最後修改：{new Date(sheet.modified_time).toLocaleDateString()}
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  選擇要使用的 Google Sheet
                </p>

                {/* 從 Drive 選擇 */}
                <Button
                  onClick={loadDriveSheets}
                  disabled={isLoadingDriveSheets}
                  variant="outline"
                  className="w-full"
                >
                  {isLoadingDriveSheets ? '載入中...' : '從 Google Drive 選擇'}
                </Button>

                {/* 建立新 Sheet */}
                <Button
                  onClick={handleCreateSheet}
                  disabled={isCreatingSheet}
                  className="w-full"
                >
                  {isCreatingSheet ? '建立中...' : '建立新的 Sheet'}
                </Button>

                {/* 分隔線 */}
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">或</span>
                  </div>
                </div>

                {/* 連結現有 Sheet */}
                <div className="space-y-2">
                  <Label htmlFor="sheet-url">手動輸入 Google Sheet URL</Label>
                  <div className="flex gap-2">
                    <Input
                      id="sheet-url"
                      placeholder="https://docs.google.com/spreadsheets/d/..."
                      value={sheetUrlInput}
                      onChange={(e) => setSheetUrlInput(e.target.value)}
                    />
                    <Button
                      onClick={handleLinkSheet}
                      disabled={isLinkingSheet || !sheetUrlInput.trim()}
                    >
                      {isLinkingSheet ? '連結中...' : '連結'}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    請確保您對該 Sheet 有編輯權限
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* API Token List (OAuth users) */}
      {isAuthenticated && authType === 'oauth' && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">API Token 管理</CardTitle>
            <CardDescription>
              管理您的 API Token，用於 Siri 捷徑等外部服務
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Generate New Token */}
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

            {/* Token List */}
            {isLoadingTokens ? (
              <div className="text-center text-muted-foreground">載入中...</div>
            ) : apiTokens.length > 0 ? (
              <div className="space-y-2">
                {apiTokens.map((t) => (
                  <div
                    key={t.id}
                    className="flex items-center justify-between bg-muted rounded-lg p-3"
                  >
                    <div>
                      <p className="text-sm font-medium">{t.description}</p>
                      <p className="text-xs text-muted-foreground">
                        建立於 {new Date(t.created_at).toLocaleDateString()}
                        {t.last_used_at && ` · 最後使用 ${new Date(t.last_used_at).toLocaleDateString()}`}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleRevokeToken(t.id)}
                      className="text-destructive hover:text-destructive"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center">
                尚未建立任何 API Token
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Legacy Token Management (non-OAuth users) */}
      {!isAuthenticated && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">API Token</CardTitle>
            <CardDescription>
              輸入 API Token 以使用記帳功能（或登入 Google 帳號）
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
            </div>
          </CardContent>
        </Card>
      )}

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
