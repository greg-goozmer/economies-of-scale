import { useEffect } from 'react';
import { Button } from 'react-bootstrap';
import { CostCard } from '../components/CostCard';
import { CostCodeFilter } from '../components/CostCodeFilter';
import { deleteOwnCost, loadCosts, setCostMinimum, setCostMaximum, useCostsDispatch, useCostsSelector } from '../store/costsStore';

export function CostTilesPage() {
  const dispatch = useCostsDispatch();
  const { items, minimum, maximum, appliedMinimum, appliedMaximum, user } = useCostsSelector(state => state.costs);
  useEffect(() => {
    void dispatch(loadCosts({ minimum: appliedMinimum, maximum: appliedMaximum }));
  }, [dispatch, user]);
  return <section className="tiles-screen" aria-labelledby="tiles-title">
    <header className="screen-header"><p className="eyebrow">Оценка экономии от масштаба</p><h1 id="tiles-title">Каталог издержек</h1></header>
    <CostCodeFilter minimum={minimum} maximum={maximum}
      onMinimumChange={value => dispatch(setCostMinimum(value))}
      onMaximumChange={value => dispatch(setCostMaximum(value))}
      onApply={() => { void dispatch(loadCosts({ minimum, maximum })); }}
      onReset={() => {
        dispatch(setCostMinimum(''));
        dispatch(setCostMaximum(''));
        void dispatch(loadCosts({ minimum: '', maximum: '' }));
      }} />
    <p className="result-count" aria-live="polite">Найдено: {items.length}</p>
    {items.length ? <div className="cost-grid">{items.map(cost => <div key={cost.cost_id}>
      <CostCard cost={cost} />
      {user && cost.is_owner === 1 && <Button className="delete-cost" onClick={() => { void dispatch(deleteOwnCost(cost.cost_id)); }}>Удалить</Button>}
    </div>)}</div> : <p className="empty-result">В выбранном диапазоне издержки не найдены.</p>}
  </section>;
}
