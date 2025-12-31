import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { getMonthlyStats, getAuthToken } from '@/services/api';
import type { TransformedStats, CategoryStat } from '@/services/api';

// 類別對應的顏色
const COLORS = [
  '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8',
  '#82CA9D', '#FFC658', '#8DD1E1', '#A4DE6C', '#D0ED57',
];

// 類別名稱對應（如果需要）
const categoryLabels: Record<string, string> = {
  '飲食': '飲食',
  '交通': '交通',
  '娛樂': '娛樂',
  '購物': '購物',
  '生活': '生活',
  '醫療': '醫療',
  '教育': '教育',
  '其他': '其他',
};

function ChevronLeftIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="m15 18-6-6 6-6" />
    </svg>
  );
}

function ChevronRightIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="m9 18 6-6-6-6" />
    </svg>
  );
}

export default function StatsPage() {
  const [stats, setStats] = useState<TransformedStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(new Date().getMonth() + 1);

  const fetchStats = async () => {
    if (!getAuthToken()) {
      toast.error('請先在設定頁面設定 API Token');
      return;
    }

    setIsLoading(true);
    try {
      const response = await getMonthlyStats(year, month);
      if (response.success) {
        setStats(response.stats);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '獲取統計資料失敗';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [year, month]);

  const handlePrevMonth = () => {
    if (month === 1) {
      setMonth(12);
      setYear(year - 1);
    } else {
      setMonth(month - 1);
    }
  };

  const handleNextMonth = () => {
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;

    // 不能超過當前月份
    if (year === currentYear && month >= currentMonth) {
      return;
    }

    if (month === 12) {
      setMonth(1);
      setYear(year + 1);
    } else {
      setMonth(month + 1);
    }
  };

  const isCurrentMonth = () => {
    const now = new Date();
    return year === now.getFullYear() && month === now.getMonth() + 1;
  };

  // 準備圓餅圖資料
  const chartData = stats?.categories.map((cat: CategoryStat) => ({
    name: categoryLabels[cat.category] || cat.category,
    value: cat.total,
    count: cat.count,
    percentage: cat.percentage,
  })) || [];

  return (
    <div className="space-y-6">
      {/* Month Selector */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <Button variant="ghost" size="icon" onClick={handlePrevMonth}>
              <ChevronLeftIcon className="h-4 w-4" />
            </Button>
            <div className="text-xl font-semibold">
              {year} 年 {month} 月
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleNextMonth}
              disabled={isCurrentMonth()}
            >
              <ChevronRightIcon className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            載入中...
          </CardContent>
        </Card>
      ) : stats ? (
        <>
          {/* Total Expense */}
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>本月總支出</CardDescription>
              <CardTitle className="text-3xl text-primary">
                NT$ {stats.total.toLocaleString()}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>共 {stats.record_count} 筆交易</span>
                <span>日均 NT$ {Math.round(stats.daily_average).toLocaleString()}</span>
              </div>
            </CardContent>
          </Card>

          {/* Pie Chart */}
          {chartData.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">類別分佈</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, payload }) => `${name} ${(payload?.percentage ?? 0).toFixed(0)}%`}
                      >
                        {chartData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value) => [`NT$ ${Number(value).toLocaleString()}`, '金額']}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-12 text-center text-muted-foreground">
                本月尚無記帳資料
              </CardContent>
            </Card>
          )}

          {/* Category List */}
          {stats.categories.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">類別明細</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {stats.categories.map((cat: CategoryStat, index: number) => (
                    <div
                      key={cat.category}
                      className="flex items-center justify-between py-2 border-b last:border-0"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        />
                        <div>
                          <div className="font-medium">
                            {categoryLabels[cat.category] || cat.category}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {cat.count} 筆
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">
                          NT$ {cat.total.toLocaleString()}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {cat.percentage.toFixed(1)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      ) : (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            請先設定 API Token
          </CardContent>
        </Card>
      )}
    </div>
  );
}
