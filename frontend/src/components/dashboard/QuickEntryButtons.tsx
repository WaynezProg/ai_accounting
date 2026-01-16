import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { QUICK_ENTRY_PRESETS, type QuickEntryPreset } from '@/services/api';

type QuickEntryButtonsProps = {
  onSubmit: (text: string) => Promise<void>;
  isLoading?: boolean;
};

type ConfirmDialogState = {
  isOpen: boolean;
  preset: QuickEntryPreset | null;
  amount: string;
};

export function QuickEntryButtons({ onSubmit, isLoading }: QuickEntryButtonsProps) {
  const [dialog, setDialog] = useState<ConfirmDialogState>({
    isOpen: false,
    preset: null,
    amount: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handlePresetClick = (preset: QuickEntryPreset) => {
    setDialog({
      isOpen: true,
      preset,
      amount: preset.defaultAmount.toString(),
    });
  };

  const handleConfirm = async () => {
    if (!dialog.preset || !dialog.amount) return;
    
    setIsSubmitting(true);
    try {
      const amount = parseInt(dialog.amount, 10);
      const text = `${dialog.preset.name} ${amount}元`;
      await onSubmit(text);
      setDialog({ isOpen: false, preset: null, amount: '' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setDialog({ isOpen: false, preset: null, amount: '' });
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base font-medium">快速記帳</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Quick Entry Buttons */}
        <div className="grid grid-cols-5 gap-2">
          {QUICK_ENTRY_PRESETS.map((preset) => (
            <Button
              key={preset.name}
              variant="outline"
              className="flex flex-col h-auto py-2 px-1"
              onClick={() => handlePresetClick(preset)}
              disabled={isLoading || isSubmitting}
            >
              <span className="text-lg">{preset.icon}</span>
              <span className="text-xs mt-1">{preset.name}</span>
            </Button>
          ))}
        </div>

        {/* Confirmation Dialog */}
        {dialog.isOpen && dialog.preset && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="bg-card rounded-lg p-4 w-72 shadow-lg">
              <div className="text-center mb-4">
                <span className="text-3xl">{dialog.preset.icon}</span>
                <h3 className="font-medium mt-2">{dialog.preset.name}</h3>
                <p className="text-xs text-muted-foreground">{dialog.preset.category}</p>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="text-sm text-muted-foreground">金額</label>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">$</span>
                    <Input
                      type="number"
                      value={dialog.amount}
                      onChange={(e) =>
                        setDialog((prev) => ({ ...prev, amount: e.target.value }))
                      }
                      min={1}
                      autoFocus
                    />
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button
                    className="flex-1"
                    onClick={handleConfirm}
                    disabled={!dialog.amount || isSubmitting}
                  >
                    {isSubmitting ? '記帳中...' : '確認記帳'}
                  </Button>
                  <Button
                    variant="outline"
                    className="flex-1"
                    onClick={handleCancel}
                    disabled={isSubmitting}
                  >
                    取消
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
