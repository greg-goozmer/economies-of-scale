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
    <Form.Label className="cost-filter-title">Код издержки</Form.Label>
    <div className="cost-code-inputs">
      <Form.Control aria-label="Код издержки от" type="number" min="0" step="1" placeholder="От" value={minimum} onChange={event => onMinimumChange(event.target.value)} />
      <span>—</span>
      <Form.Control aria-label="Код издержки до" type="number" min="0" step="1" placeholder="До" value={maximum} onChange={event => onMaximumChange(event.target.value)} />
    </div>
    <div className="cost-code-sliders">
      <Form.Range aria-label="Нижняя граница кода" min="0" max="100" value={minimum === '' ? 0 : Math.min(Number(minimum), 100)} onChange={event => onMinimumChange(event.target.value)} />
      <Form.Range aria-label="Верхняя граница кода" min="0" max="100" value={maximum === '' ? 100 : Math.min(Number(maximum), 100)} onChange={event => onMaximumChange(event.target.value)} />
    </div>
    {invalid && <p role="alert">Укажите целые коды от 0, нижняя граница не больше верхней.</p>}
    <div className="cost-filter-buttons"><Button type="submit" disabled={invalid}>Применить</Button><Button variant="outline-secondary" onClick={onReset}>Сбросить</Button></div>
  </Form>;
}
