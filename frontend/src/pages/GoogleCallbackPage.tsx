import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { exchangeGoogleCode, exchangeAuthCode } from '@/services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

/**
 * Google OAuth Callback Page
 *
 * 處理 Google OAuth 重導向回來的 callback。
 * 流程：
 * 1. 從 URL 取得 Google 授權碼 (code) 和 state
 * 2. 前端驗證 state 與 sessionStorage 中的值一致（CSRF 防護）
 * 3. 呼叫後端 /api/auth/google/exchange-code 交換 one-time code
 * 4. 用 one-time code 呼叫 /api/auth/exchange 取得 JWT
 * 5. 完成登入，跳轉至首頁
 */
export default function GoogleCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [message, setMessage] = useState('正在處理 Google 登入...');
  
  // 使用 useRef 防止 React Strict Mode 下重複執行
  const hasProcessed = useRef(false);

  useEffect(() => {
    // 防止重複執行（React Strict Mode 會執行兩次）
    if (hasProcessed.current) {
      return;
    }
    hasProcessed.current = true;

    const code = searchParams.get('code');
    const urlState = searchParams.get('state');
    const error = searchParams.get('error');

    // 清除 URL 中的敏感參數
    const clearCallbackUrl = () => {
      window.history.replaceState({}, '', '/auth/google/callback');
    };

    // 處理 Google OAuth 錯誤
    if (error) {
      clearCallbackUrl();
      setStatus('error');
      setMessage(`Google 登入失敗：${error}`);
      return;
    }

    // 檢查必要參數
    if (!code || !urlState) {
      clearCallbackUrl();
      setStatus('error');
      setMessage('登入失敗：缺少必要的認證參數');
      return;
    }

    // 前端驗證 state（CSRF 防護）
    const storedState = sessionStorage.getItem('oauth_state');
    if (urlState !== storedState) {
      clearCallbackUrl();
      sessionStorage.removeItem('oauth_state');
      setStatus('error');
      setMessage('登入失敗：安全驗證失敗，請重新登入');
      console.error('OAuth state mismatch:', { urlState, storedState });
      return;
    }

    // 驗證成功，清除 sessionStorage 中的 state
    sessionStorage.removeItem('oauth_state');
    clearCallbackUrl();

    const handleGoogleCallback = async () => {
      try {
        // Step 1: 交換 Google 授權碼為 one-time code（不再傳送 state，後端不驗證）
        setMessage('正在驗證 Google 授權...');
        const googleResponse = await exchangeGoogleCode(code);

        // Step 2: 用 one-time code 交換 JWT
        setMessage('正在建立登入狀態...');
        const session = await exchangeAuthCode(googleResponse.code);

        // Step 3: 完成登入
        login(session.access_token, {
          refreshToken: session.refresh_token,
          expiresAt: session.access_token_expires_at,
        });

        setStatus('success');
        setMessage(googleResponse.new_user ? '歡迎加入！正在跳轉...' : '登入成功！正在跳轉...');

        // 跳轉至首頁
        setTimeout(() => {
          navigate('/', { replace: true });
        }, 1500);
      } catch (error) {
        console.error('Google OAuth callback failed:', error);
        setStatus('error');

        // 處理不同類型的錯誤
        if (error instanceof Error) {
          setMessage(`登入失敗：${error.message}`);
        } else {
          setMessage('登入失敗：發生未知錯誤');
        }
      }
    };

    handleGoogleCallback();
  }, [searchParams, login, navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle>
            {status === 'processing' && '處理中...'}
            {status === 'success' && '登入成功'}
            {status === 'error' && '登入失敗'}
          </CardTitle>
          <CardDescription>{message}</CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center">
          {status === 'processing' && (
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          )}
          {status === 'success' && (
            <div className="text-4xl text-green-500">✓</div>
          )}
          {status === 'error' && (
            <div className="text-center space-y-4">
              <div className="text-4xl text-red-500">✕</div>
              <button
                onClick={() => navigate('/')}
                className="text-primary hover:underline"
              >
                返回首頁
              </button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
