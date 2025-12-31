import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [message, setMessage] = useState('正在處理登入...');

  useEffect(() => {
    const token = searchParams.get('token');
    const newUser = searchParams.get('new_user');

    if (token) {
      // Save token and update auth state
      login(token);
      setStatus('success');
      setMessage(newUser === '1' ? '歡迎加入！正在跳轉...' : '登入成功！正在跳轉...');

      // Redirect to home after a short delay
      setTimeout(() => {
        navigate('/', { replace: true });
      }, 1500);
    } else {
      setStatus('error');
      setMessage('登入失敗：未收到認證資訊');
    }
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
            <div className="text-4xl">✓</div>
          )}
          {status === 'error' && (
            <div className="text-center space-y-4">
              <div className="text-4xl">✕</div>
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
