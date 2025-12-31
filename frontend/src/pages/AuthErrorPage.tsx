import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function AuthErrorPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const errorMessage = searchParams.get('message') || '未知錯誤';

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-destructive">登入失敗</CardTitle>
          <CardDescription>無法完成 Google 帳號登入</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-destructive/10 text-destructive p-4 rounded-lg text-sm">
            {errorMessage}
          </div>
          <div className="flex justify-center gap-4">
            <Button variant="outline" onClick={() => navigate('/')}>
              返回首頁
            </Button>
            <Button onClick={() => window.location.href = '/api/auth/google/login'}>
              重試登入
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
