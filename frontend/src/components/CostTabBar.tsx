import { Nav, Navbar } from 'react-bootstrap';
import { useLocation, useNavigate } from 'react-router-dom';
import type { CostItem } from '../modules/costsMock';
import { CostIcon } from './CostIcon';

export function CostTabBar({ costs }: { costs: CostItem[] }) {
  const location = useLocation();
  const navigate = useNavigate();
  return <Navbar className="cost-tabbar" aria-label="Навигация по издержкам"><Nav>
    <Nav.Link as="button" active={location.pathname.startsWith('/costs/feed')} disabled={!costs.length} onClick={() => navigate(`/costs/feed/${costs[0].cost_id}`)}><CostIcon name="feed" />Лента</Nav.Link>
    <Nav.Link as="button" disabled><CostIcon name="add" />Добавление</Nav.Link>
    <Nav.Link as="button" active={location.pathname === '/costs'} onClick={() => navigate('/costs')}><CostIcon name="tiles" />Плитка</Nav.Link>
    <Nav.Link as="button" disabled><CostIcon name="login" />Вход</Nav.Link>
  </Nav></Navbar>;
}
