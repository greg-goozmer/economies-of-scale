import { Alert, Spinner } from 'react-bootstrap';
import { Navigate, Route, Routes } from 'react-router-dom';
import { CostTabBar } from './components/CostTabBar';
import { CostFeedPage } from './pages/CostFeedPage';
import { CostTilesPage } from './pages/CostTilesPage';
import { CostLoginPage } from './pages/CostLoginPage';
import { CostDraftPage } from './pages/CostDraftPage';
import { clearCostError, useCostsDispatch, useCostsSelector } from './store/costsStore';

export default function App() {
  const dispatch = useCostsDispatch();
  const { pending, authBusy, error, mock } = useCostsSelector(state => state.costs);
  const busy = pending > 0 || authBusy;
  return <div className="cost-shell" aria-busy={busy}>
    <fieldset className="cost-app-controls" disabled={busy}>
      <main className="cost-content">
        {error && <Alert variant="danger" dismissible onClose={() => dispatch(clearCostError())}>{error}</Alert>}
        {mock && <p className="cost-offline" role="status">Сервер недоступен · демонстрационные данные</p>}
        <Routes>
          <Route path="/" element={<Navigate to="/costs" replace />} />
          <Route path="/costs" element={<CostTilesPage />} />
          <Route path="/costs/feed" element={<CostFeedPage />} />
          <Route path="/costs/feed/:costId" element={<CostFeedPage />} />
          <Route path="/costs/login" element={<CostLoginPage />} />
          <Route path="/costs/draft" element={<CostDraftPage />} />
          <Route path="*" element={<Navigate to="/costs" replace />} />
        </Routes>
      </main>
      <CostTabBar />
    </fieldset>
    {busy && <div className="cost-loading" role="status"><Spinner animation="border" /><span>Загрузка…</span></div>}
  </div>;
}
