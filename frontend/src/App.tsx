import { useState } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { CostTabBar } from './components/CostTabBar';
import { COSTS_MOCK } from './modules/costsMock';
import { CostFeedPage } from './pages/CostFeedPage';
import { CostTilesPage } from './pages/CostTilesPage';

export default function App() {
  const [costs, setCosts] = useState(COSTS_MOCK);
  // Общие данные передаются через props. Context и Redux не используются.
  return <div className="cost-shell"><main className="cost-content"><Routes>
    <Route path="/" element={<Navigate to="/costs" replace />} />
    <Route path="/costs" element={<CostTilesPage costs={costs} onCostsChange={setCosts} />} />
    <Route path="/costs/feed" element={costs.length ? <Navigate to={`/costs/feed/${costs[0].cost_id}`} replace /> : <Navigate to="/costs" replace />} />
    <Route path="/costs/feed/:costId" element={<CostFeedPage costs={costs} />} />
    <Route path="*" element={<Navigate to="/costs" replace />} />
  </Routes></main><CostTabBar costs={costs} /></div>;
}
