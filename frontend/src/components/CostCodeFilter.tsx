import { Button, Form } from 'react-bootstrap';

interface CostCodeFilterProps {
  minimum: string;
  maximum: string;
  onMinimumChange: (value: string) => void;
  onMaximumChange: (value: string) => void;
  onApply: () => void;
  onReset: () => void;
}

export function CostCodeFilter({ minimum, maximum, onMinimumChange, onMaximumChange, onApply, onReset }: CostCodeFilterProps) {
  const invalid = (minimum !== '' && (!Number.isInteger(Number(minimum)) || Number(minimum) < 0)) ||
    (maximum !== '' && (!Number.isInteger(Number(maximum)) || Number(maximum) < 0)) ||
    (minimum !== '' && maximum !== '' && Number(minimum) > Number(maximum));
  return <Form className="cost-filter" onSubmit={event => { event.preventDefault(); if (!invalid) onApply(); }}>
    <div className="filter-heading"><span>Диапазон кодов</span>
      {(minimum !== '' || maximum !== '') && <Button variant="link" className="filter-reset" onClick={onReset}>Сбросить</Button>}</div>
    <div className="filter-values">
      <label><span>От</span><Form.Control aria-label="Код издержки от" type="number" min="0" step="1" placeholder="20" value={minimum} onChange={event => onMinimumChange(event.target.value)} /></label>
      <label><span>До</span><Form.Control aria-label="Код издержки до" type="number" min="0" step="1" placeholder="44" value={maximum} onChange={event => onMaximumChange(event.target.value)} /></label>
    </div>
    <div className="dual-range"><div className="dual-range__track" aria-hidden="true" />
      <Form.Range aria-label="Нижняя граница кода" min="20" max="44" value={minimum === '' ? 20 : Math.max(20, Math.min(Number(minimum), 44))} onChange={event => onMinimumChange(event.target.value)} />
      <Form.Range aria-label="Верхняя граница кода" min="20" max="44" value={maximum === '' ? 44 : Math.max(20, Math.min(Number(maximum), 44))} onChange={event => onMaximumChange(event.target.value)} />
    </div>
    {invalid && <p role="alert">Укажите целые коды от 0, нижняя граница не больше верхней.</p>}
    <Button type="submit" disabled={invalid}>Применить</Button>
  </Form>;
}
