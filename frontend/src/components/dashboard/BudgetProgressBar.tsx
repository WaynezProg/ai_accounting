import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { BudgetStatus } from '@/services/api';

type BudgetProgressBarProps = {
  budget: BudgetStatus | null;
  isLoading?: boolean;
  onSetBudget?: (amount: number | null) => Promise<void>;
};

function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse bg-muted rounded ${className}`} />;
}

export function BudgetProgressBar({
  budget,
  isLoading,
  onSetBudget,
}: BudgetProgressBarProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [budgetInput, setBudgetInput] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const handleSaveBudget = async () => {
    if (!onSetBudget) return;
    
    setIsSaving(true);
    try {
      const amount = budgetInput.trim() ? parseInt(budgetInput, 10) : null;
      await onSetBudget(amount);
      setIsEditing(false);
      setBudgetInput('');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">本月預算</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-2 w-full" />
        </CardContent>
      </Card>
    );
  }

  // Show edit form if no budget set or editing
  // Use == null to distinguish between "not set" (null/undefined) and "set to 0"
  if (budget?.monthly_limit == null || isEditing) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">本月預算</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {isEditing ? (
            <>
              <div className="flex gap-2">
                <Input
                  type="number"
                  placeholder="輸入預算金額"
                  value={budgetInput}
                  onChange={(e) => setBudgetInput(e.target.value)}
                  min={0}
                />
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={handleSaveBudget}
                  disabled={isSaving}
                  className="flex-1"
                >
                  {isSaving ? '儲存中...' : '儲存'}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setIsEditing(false);
                    setBudgetInput('');
                  }}
                  className="flex-1"
                >
                  取消
                </Button>
              </div>
            </>
          ) : (
            <>
              <p className="text-sm text-muted-foreground">尚未設定預算</p>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setIsEditing(true)}
              >
                設定預算
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    );
  }

  // Calculate progress
  const percentage = budget.percentage ?? 0;
  const isOverBudget = percentage > 100;
  const progressColor = isOverBudget
    ? 'bg-destructive'
    : percentage > 80
      ? 'bg-yellow-500'
      : 'bg-primary';

  return (
    <Card>
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <CardTitle className="text-base font-medium">本月預算</CardTitle>
        <Button
          size="sm"
          variant="ghost"
          className="h-7 text-xs"
          onClick={() => {
            setBudgetInput(budget.monthly_limit.toString());
            setIsEditing(true);
          }}
        >
          編輯
        </Button>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>
            已花費 ${budget.spent.toLocaleString()}
          </span>
          <span className="text-muted-foreground">
            / ${budget.monthly_limit.toLocaleString()}
          </span>
        </div>
        
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className={`h-full ${progressColor} rounded-full transition-all`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>

        <div className="flex justify-between text-xs text-muted-foreground">
          <span>{percentage.toFixed(0)}% 已使用</span>
          {budget.remaining !== null && !Number.isNaN(budget.remaining) && (
            <span className={isOverBudget ? 'text-destructive' : ''}>
              {isOverBudget
                ? `超支 $${Math.abs(budget.remaining).toLocaleString()}`
                : `剩餘 $${budget.remaining.toLocaleString()}`}
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
