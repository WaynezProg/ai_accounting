import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { MonthSummary } from '@/services/api';

type MonthSummaryCardProps = {
  summary: MonthSummary | null;
  isLoading?: boolean;
};

function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse bg-muted rounded ${className}`} />;
}

export function MonthSummaryCard({ summary, isLoading }: MonthSummaryCardProps) {
  const currentMonth = new Date().toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">{currentMonth}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-4 w-24" />
          <div className="space-y-2">
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-3/4" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!summary) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">{currentMonth}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">尚無資料</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-medium">{currentMonth}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <div className="text-2xl font-bold text-primary">
            ${summary.total.toLocaleString()}
          </div>
          <div className="text-xs text-muted-foreground">
            {summary.record_count} 筆記錄
          </div>
        </div>

        {summary.top_categories.length > 0 && (
          <div className="space-y-1.5">
            <div className="text-xs text-muted-foreground">支出分佈</div>
            {summary.top_categories.map((cat) => (
              <div key={cat.category} className="flex items-center gap-2">
                <div className="flex-1">
                  <div className="flex justify-between text-xs mb-0.5">
                    <span>{cat.category}</span>
                    <span className="text-muted-foreground">
                      ${cat.total.toLocaleString()} ({cat.percentage.toFixed(0)}%)
                    </span>
                  </div>
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ width: `${cat.percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
