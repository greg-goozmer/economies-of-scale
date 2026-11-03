import { Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import type { CostItem } from '../modules/costsMock';
import { CostImage } from './CostMedia';

export function CostCard({ cost }: { cost: CostItem }) {
  return <Card as={Link} to={`/costs/feed/${cost.cost_id}`} className="cost-card">
    <CostImage url={cost.cost_image_url} name={cost.cost_name} />
    <Card.Body><small>КОД {cost.cost_code}</small><Card.Title as="h2">{cost.cost_name}</Card.Title>
      <div className="cost-card-meta"><span>{cost.cost_behavior === 'fixed' ? 'Постоянные' : 'Переменные'}</span><span>♡ {cost.like_count}</span></div>
    </Card.Body></Card>;
}
