import { CostCard } from '../components/CostCard';
import { CostCodeFilter } from '../components/CostCodeFilter';
import { COSTS_MOCK, filterCosts, type CostItem } from '../modules/costsMock';

interface CostTilesProps {
  costs: CostItem[]; onCostsChange: (costs: CostItem[]) => void;
  minimum: string; maximum: string;
  onMinimumChange: (value: string) => void; onMaximumChange: (value: string) => void;
}

export function CostTilesPage({ costs, onCostsChange, minimum, maximum, onMinimumChange, onMaximumChange }: CostTilesProps) {
  return <section className="tiles-screen" aria-labelledby="tiles-title">
    <header className="screen-header"><p className="eyebrow">Оценка экономии от масштаба</p><h1 id="tiles-title">Каталог издержек</h1></header>
    <CostCodeFilter minimum={minimum} maximum={maximum} onMinimumChange={onMinimumChange} onMaximumChange={onMaximumChange}
      onApply={() => onCostsChange(filterCosts(COSTS_MOCK, minimum, maximum))}
      onReset={() => { onMinimumChange(''); onMaximumChange(''); onCostsChange(COSTS_MOCK); }} />
    <p className="result-count" aria-live="polite">Найдено: {costs.length}</p>
    {costs.length ? <div className="cost-grid">{costs.map(cost => <CostCard key={cost.cost_id} cost={cost} />)}</div> : <p className="empty-result" role="status">В выбранном диапазоне издержки не найдены.</p>}
  </section>;
}
