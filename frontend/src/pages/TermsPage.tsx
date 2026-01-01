import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-3xl px-4 py-8">
        <Link to="/">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回首頁
          </Button>
        </Link>

        <h1 className="mb-8 text-3xl font-bold">服務條款</h1>

        <div className="prose prose-gray dark:prose-invert max-w-none space-y-6">
          <p className="text-muted-foreground">最後更新日期：2026 年 1 月 1 日</p>

          <section>
            <h2 className="text-xl font-semibold">1. 服務說明</h2>
            <p>
              語音記帳助手（以下簡稱「本服務」）是一個整合語音輸入、AI 解析和 Google Sheets 的個人記帳工具。本服務協助您透過語音或文字快速記錄支出，並自動儲存至您的 Google Sheets。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">2. 使用條件</h2>
            <p>使用本服務，您需要：</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>擁有有效的 Google 帳號</li>
              <li>同意授權本服務存取您的 Google Sheets</li>
              <li>遵守本服務條款</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">3. 使用者責任</h2>
            <p>使用本服務時，您同意：</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>提供真實、準確的資訊</li>
              <li>妥善保管您的帳號憑證</li>
              <li>不將本服務用於任何非法目的</li>
              <li>不嘗試破壞或干擾服務運作</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">4. 服務內容</h2>
            <p>本服務提供以下功能：</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>語音/文字記帳輸入</li>
              <li>AI 自動解析記帳內容</li>
              <li>Google Sheets 資料儲存</li>
              <li>支出統計與分析</li>
              <li>自然語言查詢</li>
              <li>Siri 捷徑整合</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">5. 免責聲明</h2>
            <p>
              本服務按「現況」提供，不提供任何明示或暗示的保證。我們不保證：
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>服務將持續不中斷或無錯誤</li>
              <li>AI 解析結果 100% 準確</li>
              <li>資料永久保存（資料儲存在您的 Google Sheets）</li>
            </ul>
            <p className="mt-4">
              本服務提供的理財建議僅供參考，不構成專業財務建議。請根據您的實際情況做出財務決策。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">6. 責任限制</h2>
            <p>
              在法律允許的最大範圍內，我們對於因使用或無法使用本服務而導致的任何直接、間接、附帶、特殊或後果性損害不承擔責任。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">7. 第三方服務</h2>
            <p>
              本服務使用以下第三方服務：
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Google OAuth - 用於使用者認證</li>
              <li>Google Sheets API - 用於資料儲存</li>
              <li>OpenAI API - 用於 AI 解析和語音合成</li>
            </ul>
            <p className="mt-4">
              使用這些第三方服務時，您也需要遵守其各自的服務條款。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">8. 智慧財產權</h2>
            <p>
              本服務的程式碼以 MIT 授權開源。您的記帳資料歸您所有。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">9. 服務變更與終止</h2>
            <p>
              我們保留隨時修改、暫停或終止服務的權利，恕不另行通知。我們建議您定期備份您的 Google Sheets 資料。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">10. 條款變更</h2>
            <p>
              我們可能會不時更新本服務條款。繼續使用本服務即表示您接受更新後的條款。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">11. 準據法</h2>
            <p>
              本服務條款受中華民國法律管轄。
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">12. 聯絡方式</h2>
            <p>
              如有任何問題，請透過 GitHub Issues 聯絡我們。
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
