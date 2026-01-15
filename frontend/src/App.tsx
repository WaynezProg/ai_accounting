import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import HomePage from '@/pages/HomePage';
import StatsPage from '@/pages/StatsPage';
import QueryPage from '@/pages/QueryPage';
import SettingsPage from '@/pages/SettingsPage';
import AuthCallbackPage from '@/pages/AuthCallbackPage';
import GoogleCallbackPage from '@/pages/GoogleCallbackPage';
import AuthErrorPage from '@/pages/AuthErrorPage';
import PrivacyPage from '@/pages/PrivacyPage';
import TermsPage from '@/pages/TermsPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-center" richColors />
        <Routes>
          {/* OAuth callback routes (outside main layout) */}
          <Route path="/auth/callback" element={<AuthCallbackPage />} />
          <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />
          <Route path="/auth/error" element={<AuthErrorPage />} />

          {/* Legal pages (outside main layout) */}
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/terms" element={<TermsPage />} />

          {/* Main app routes */}
          <Route path="/" element={<AppLayout />}>
            <Route index element={<HomePage />} />
            <Route path="stats" element={<StatsPage />} />
            <Route path="query" element={<QueryPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
