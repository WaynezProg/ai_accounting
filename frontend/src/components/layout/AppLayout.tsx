import { Outlet, Link } from 'react-router-dom';
import BottomNav from './BottomNav';

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
        <div className="mx-auto max-w-md px-4 py-3">
          <h1 className="text-xl font-bold text-center">語音記帳助手</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-md px-4 py-4 pb-24">
        <Outlet />
      </main>

      {/* Footer Links */}
      <footer className="fixed bottom-16 left-0 right-0 bg-background/95 backdrop-blur border-t">
        <div className="mx-auto max-w-md px-4 py-2 flex justify-center gap-4 text-xs text-muted-foreground">
          <Link to="/privacy" className="hover:text-foreground transition-colors">
            隱私權政策
          </Link>
          <span>|</span>
          <Link to="/terms" className="hover:text-foreground transition-colors">
            服務條款
          </Link>
        </div>
      </footer>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  );
}
