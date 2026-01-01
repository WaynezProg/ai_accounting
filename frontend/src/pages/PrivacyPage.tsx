import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-3xl px-4 py-8">
        <Link to="/">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回首頁
          </Button>
        </Link>

        <h1 className="mb-8 text-3xl font-bold">隱私權政策</h1>

        <div className="prose prose-gray dark:prose-invert max-w-none space-y-6">
          <p className="text-muted-foreground">最後更新日期：2026 年 1 月 1 日</p>

          <section>
            <h2 className="text-xl font-semibold">1. 簡介</h2>
            <p>
              語音記帳助手（以下簡稱「本服務」）重視您的隱私。本隱私權政策說明我們如何收集、使用和保護您的個人資料。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">2. 我們收集的資料</h2>
            <p>當您使用本服務時，我們可能收集以下資料：</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Google 帳號資訊</strong>：當您使用 Google 登入時，我們會取得您的電子郵件地址、姓名和個人資料照片。
              </li>
              <li>
                <strong>記帳資料</strong>：您輸入的記帳內容，包括日期、金額、類別和描述。
              </li>
              <li>
                <strong>Google Sheets 存取</strong>：我們會存取您授權的 Google Sheets 以儲存記帳資料。
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">3. 資料使用方式</h2>
            <p>我們使用您的資料來：</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>提供記帳服務功能</li>
              <li>將記帳資料儲存至您的 Google Sheets</li>
              <li>產生統計報表和分析</li>
              <li>改善服務品質</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">4. 資料儲存</h2>
            <p>
              您的記帳資料主要儲存在您自己的 Google Sheets 中。我們的伺服器僅儲存必要的帳號關聯資訊，不會長期保存您的詳細記帳內容。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">5. 資料分享</h2>
            <p>
              我們不會將您的個人資料出售或分享給第三方，除非：
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>經您明確同意</li>
              <li>法律要求</li>
              <li>使用 OpenAI API 處理您的記帳文字（僅傳送記帳內容，不含個人識別資訊）</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">6. 資料安全</h2>
            <p>
              我們採用業界標準的安全措施保護您的資料，包括：
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>HTTPS 加密傳輸</li>
              <li>JWT Token 認證</li>
              <li>安全的雲端基礎設施（Google Cloud Platform）</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">7. 您的權利</h2>
            <p>您有權：</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>存取您的個人資料</li>
              <li>要求刪除您的帳號和相關資料</li>
              <li>撤銷 Google 授權（可在 Google 帳號設定中操作）</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">8. Cookie</h2>
            <p>
              本服務使用 Local Storage 儲存認證 Token，不使用追蹤型 Cookie。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">9. 政策變更</h2>
            <p>
              我們可能會不時更新本隱私權政策。重大變更時，我們會在服務中通知您。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">10. 聯絡我們</h2>
            <p>
              如有任何隱私相關問題，請透過 GitHub Issues 聯絡我們。
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
