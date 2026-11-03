import { Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import type { CostItem } from '../modules/costsMock';
import { CostImage } from './CostMedia';
import { CostIcon } from './CostIcon';

export function CostCard({ cost }: { cost: CostItem }) {
  return <Card as={Link} to={`/costs/feed/${cost.cost_id}`} className="cost-card">
    <CostImage url={cost.cost_image_url} name={cost.cost_name} />
    <Card.Body className="cost-card__body"><Card.Title as="h2">{cost.cost_name}</Card.Title>
      <div className="cost-card__meta"><span>Код {cost.cost_code}</span><span className="card-likes" aria-label={`Лайков: ${cost.like_count}`}><CostIcon name="heart" />{cost.like_count}</span></div>
    </Card.Body></Card>;
}
