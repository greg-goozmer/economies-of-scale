import { useState } from 'react';
import { Nav, Navbar } from 'react-bootstrap';
import { useLocation, useNavigate } from 'react-router-dom';
import { CostIcon } from './CostIcon';
import { costUsersApi, costError } from '../api/costsClient';
import { resetCostUser, setCostAuthBusy, useCostsDispatch, useCostsSelector, loadCosts } from '../store/costsStore';

export function CostTabBar() {
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useCostsDispatch();
  const user = useCostsSelector(state => state.costs.user);
  const [error, setError] = useState('');
  async function logout() {
    dispatch(setCostAuthBusy(true));
    setError('');
    try {
      await costUsersApi.post('/logout');
      dispatch(resetCostUser());
      navigate('/costs');
      void dispatch(loadCosts({ minimum: '', maximum: '' }));
    } catch (error) { setError(costError(error)); }
    finally { dispatch(setCostAuthBusy(false)); }
  }
  return <><Navbar className="cost-tabbar" aria-label="Навигация по издержкам"><Nav>
    <Nav.Link as="button" active={location.pathname.startsWith('/costs/feed')} onClick={() => navigate('/costs/feed')}><CostIcon name="feed" />Лента</Nav.Link>
    <Nav.Link as="button" disabled={!user} active={location.pathname === '/costs/draft'} onClick={() => navigate('/costs/draft')}><CostIcon name="add" />Добавление</Nav.Link>
    <Nav.Link as="button" active={location.pathname === '/costs'} onClick={() => navigate('/costs')}><CostIcon name="tiles" />Плитка</Nav.Link>
    <Nav.Link as="button" active={location.pathname === '/costs/login'} onClick={() => user ? void logout() : navigate('/costs/login')}><CostIcon name="login" />{user ? 'Выход' : 'Вход'}</Nav.Link>
  </Nav></Navbar>{error && <p className="cost-navbar-error" role="alert">{error}</p>}</>;
}
