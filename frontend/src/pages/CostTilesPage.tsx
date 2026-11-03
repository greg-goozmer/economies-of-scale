import { useState } from 'react';
import { CostCard } from '../components/CostCard';
import { CostCodeFilter } from '../components/CostCodeFilter';
import { COSTS_MOCK, filterCosts, type CostItem } from '../modules/costsMock';

interface CostTilesProps { costs: CostItem[]; onCostsChange: (costs: CostItem[]) => void }

export function CostTilesPage({ costs, onCostsChange }: CostTilesProps) {
  const [minimum, setMinimum] = useState('');
  const [maximum, setMaximum] = useState('');
  return <section className="cost-tiles">
    <header><span className="cost-brand">МАСШТАБ <span>↗</span></span><p>Постоянные и переменные</p><h1>Издержки</h1></header>
    <CostCodeFilter minimum={minimum} maximum={maximum} onMinimumChange={setMinimum} onMaximumChange={setMaximum}
      onApply={() => onCostsChange(filterCosts(COSTS_MOCK, minimum, maximum))}
      onReset={() => { setMinimum(''); setMaximum(''); onCostsChange(COSTS_MOCK); }} />
    <div className="cost-list-heading"><h2>Виды издержек</h2><span aria-live="polite">Найдено: {costs.length}</span></div>
    {costs.length ? <div className="cost-grid">{costs.map(cost => <CostCard key={cost.cost_id} cost={cost} />)}</div> : <p role="status">Издержки с таким кодом не найдены. Измените диапазон или нажмите «Сбросить».</p>}
  </section>;
}
