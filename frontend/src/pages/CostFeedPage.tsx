import { useEffect, useState } from 'react';
import { Button } from 'react-bootstrap';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { CostVideo } from '../components/CostMedia';
import { CostIcon } from '../components/CostIcon';
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
  if (!cost) return <section className="screen-message"><h1>Издержка не найдена</h1><Link to="/costs">Вернуться к плитке</Link></section>;
  const following = nextCost(costs, cost.cost_id);
  return <section className="feed-screen" aria-label="Лента издержек">
    <CostVideo key={cost.cost_id} url={cost.cost_video_url} image={cost.cost_image_url} />
    <div className="feed-shade" aria-hidden="true" />
    <div className="feed-copy"><h1>{cost.cost_name}</h1>
      <p className="feed-parameters">{cost.cost_behavior === 'fixed' ? 'Постоянные' : 'Переменные'} · Код {cost.cost_code}</p>
      <p className={expanded ? 'description-full' : 'description-preview'}>{cost.cost_description}</p>
      <Button className="description-toggle" aria-expanded={expanded} onClick={() => setExpanded(!expanded)}>{expanded ? 'Свернуть' : 'Ещё'}</Button>
    </div>
    <aside className="feed-actions" aria-label="Действия с карточкой">
      <div className="feed-action" aria-label={`Лайков: ${cost.like_count}`}><span className="feed-action__icon"><CostIcon name="heart" /></span><span className="feed-action__label">{cost.like_count}</span></div>
      <div className="parameter-disclosure">
        <Button className="feed-action" aria-label="Параметры издержки" aria-expanded={parameters} onClick={() => setParameters(!parameters)}><span className="feed-action__icon"><CostIcon name="parameters" /></span><span className="feed-action__label">Параметры</span></Button>
        {parameters && <div className="parameter-panel"><h2>Параметры</h2><dl>
          <div><dt>Вид издержек</dt><dd>{cost.cost_behavior === 'fixed' ? 'Постоянные' : 'Переменные'}</dd></div>
          <div><dt>Код издержки</dt><dd>{cost.cost_code}</dd></div>
        </dl></div>}
      </div>
      <Button className="feed-action" aria-label="Следующая издержка" disabled={!following} onClick={() => following && navigate(`/costs/feed/${following.cost_id}`)}><span className="feed-action__icon"><CostIcon name="next" /></span><span className="feed-action__label">Далее</span></Button>
    </aside>
  </section>;
}
