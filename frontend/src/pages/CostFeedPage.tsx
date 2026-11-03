import { useEffect, useState } from 'react';
import { Button } from 'react-bootstrap';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { CostVideo } from '../components/CostMedia';
import { COSTS_MOCK, nextCost, type CostItem } from '../modules/costsMock';

export function CostFeedPage({ costs }: { costs: CostItem[] }) {
  const { costId } = useParams();
  const navigate = useNavigate();
  const [expanded, setExpanded] = useState(false);
  const [parameters, setParameters] = useState(false);
  const cost = COSTS_MOCK.find(item => String(item.cost_id) === costId);
  // Эффект обновления и cleanup: при смене карточки сбрасываем раскрытия и заголовок.
  useEffect(() => {
    setExpanded(false);
    setParameters(false);
    document.title = cost ? `${cost.cost_name} — Масштаб` : 'Издержка не найдена — Масштаб';
    return () => { document.title = 'Масштаб — издержки'; };
  }, [costId, cost]);
  if (!cost) return <section className="cost-tiles"><h1>Издержка не найдена</h1><Link to="/costs">Вернуться к плитке</Link></section>;
  const following = nextCost(costs, cost.cost_id);
  return <section className="cost-feed">
    <CostVideo key={cost.cost_id} url={cost.cost_video_url} image={cost.cost_image_url} />
    <div className="cost-feed-shade" />
    <div className="cost-feed-brand">МАСШТАБ ↗ <span>Лента издержек</span></div>
    <div className="cost-feed-actions">
      <Button variant="dark" aria-label="Параметры издержки" aria-expanded={parameters} onClick={() => setParameters(!parameters)}>⚙</Button>
      <div className="cost-feed-likes" title="Лайки доступны после входа в ЛР6">♡<small>{cost.like_count}</small></div>
    </div>
    {parameters && <div className="cost-parameters"><b>Параметры</b><p>Код издержки: {cost.cost_code}</p><p>Тип: {cost.cost_behavior === 'fixed' ? 'Постоянные' : 'Переменные'}</p></div>}
    <div className="cost-feed-copy"><small>ВИДЫ ИЗДЕРЖЕК</small><h1>{cost.cost_name}</h1>
      <p className={expanded ? '' : 'cost-description-short'}>{cost.cost_description}</p>
      <Button variant="link" className="cost-more" onClick={() => setExpanded(!expanded)}>{expanded ? 'Свернуть' : 'Ещё'}</Button>
      <Button className="cost-next" disabled={!following} onClick={() => following && navigate(`/costs/feed/${following.cost_id}`)}>Следующая издержка →</Button>
    </div>
  </section>;
}
