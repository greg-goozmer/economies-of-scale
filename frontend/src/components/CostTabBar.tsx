import { Nav, Navbar } from 'react-bootstrap';
import { useLocation, useNavigate } from 'react-router-dom';
import type { CostItem } from '../modules/costsMock';

export function CostTabBar({ costs }: { costs: CostItem[] }) {
  const location = useLocation();
  const navigate = useNavigate();
  return <Navbar className="cost-tabbar" aria-label="Навигация по издержкам"><Nav>
    <Nav.Link as="button" active={location.pathname.startsWith('/costs/feed')} disabled={!costs.length} onClick={() => navigate(`/costs/feed/${costs[0].cost_id}`)}><span>▷</span>Лента</Nav.Link>
    <Nav.Link as="button" disabled title="Добавление доступно начиная с ЛР6"><span>＋</span>Добавление</Nav.Link>
    <Nav.Link as="button" active={location.pathname === '/costs'} onClick={() => navigate('/costs')}><span>▦</span>Плитка</Nav.Link>
    <Nav.Link as="button" disabled title="Вход доступен начиная с ЛР6"><span>♙</span>Вход</Nav.Link>
  </Nav></Navbar>;
}
