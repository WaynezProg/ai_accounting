import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { DailyTrend } from '@/services/api';

type TrendSparklineProps = {
  data: DailyTrend[];
  isLoading?: boolean;
};

function Skeleton({ className, style }: { className?: string; style?: React.CSSProperties }) {
  return <div className={`animate-pulse bg-muted rounded ${className}`} style={style} />;
}

function formatDay(dateStr: string): string {
  const date = new Date(dateStr);
  const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
  return weekdays[date.getDay()];
}

export function TrendSparkline({ data, isLoading }: TrendSparklineProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">7 日消費趨勢</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-end justify-between gap-1 h-20">
            {[1, 2, 3, 4, 5, 6, 7].map((i) => (
              <Skeleton key={i} className="w-full" style={{ height: `${Math.random() * 60 + 20}%` }} />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (data.length === 0) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">7 日消費趨勢</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground text-center py-4">
            尚無資料
          </p>
        </CardContent>
      </Card>
    );
  }

  // Calculate max value for scaling
  const maxValue = Math.max(...data.map((d) => d.total), 1);
  const today = new Date().toDateString();

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-medium">7 日消費趨勢</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-end justify-between gap-1 h-20">
          {data.map((day) => {
            const isToday = new Date(day.date).toDateString() === today;
            const heightPercent = maxValue > 0 ? (day.total / maxValue) * 100 : 0;
            const hasData = day.total > 0;

            return (
              <div
                key={day.date}
                className="flex flex-col items-center flex-1"
                title={`${day.date}: $${day.total.toLocaleString()}`}
              >
                <div className="w-full flex items-end justify-center h-16">
                  <div
                    className={`w-full max-w-6 rounded-t transition-all ${
                      isToday
                        ? 'bg-primary'
                        : hasData
                          ? 'bg-primary/40'
                          : 'bg-muted'
                    }`}
                    style={{
                      height: hasData ? `${Math.max(heightPercent, 8)}%` : '4px',
                    }}
                  />
                </div>
                <div
                  className={`text-[10px] mt-1 ${
                    isToday ? 'font-medium text-primary' : 'text-muted-foreground'
                  }`}
                >
                  {formatDay(day.date)}
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Legend */}
        <div className="flex justify-between text-xs text-muted-foreground mt-2">
          <span>
            平均 ${(data.reduce((sum, d) => sum + d.total, 0) / data.length).toFixed(0)}/天
          </span>
          <span>
            最高 ${Math.max(...data.map((d) => d.total)).toLocaleString()}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
