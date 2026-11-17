import { useEffect, useState } from 'react';
import { Button } from 'react-bootstrap';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { CostVideo } from '../components/CostMedia';
import { CostIcon } from '../components/CostIcon';
import { costMediaUrl } from '../api/costsClient';
import { changeCostLike, loadCostFeed, useCostsDispatch, useCostsSelector } from '../store/costsStore';

export function CostFeedPage() {
  const { costId } = useParams();
  const navigate = useNavigate();
  const dispatch = useCostsDispatch();
  const { feed: cost, user, pending } = useCostsSelector(state => state.costs);
  const [expanded, setExpanded] = useState(false);
  const [parameters, setParameters] = useState(false);
  useEffect(() => {
    setExpanded(false);
    setParameters(false);
    const request = dispatch(loadCostFeed({ cost_id: costId ? Number(costId) : undefined }));
    return () => { request.abort(); document.title = 'Масштаб — издержки'; };
  }, [costId, dispatch, user]);
  useEffect(() => { if (cost) document.title = `${cost.cost_name} — Масштаб`; }, [cost]);
  async function next() {
    if (!cost) return;
    const result = await dispatch(loadCostFeed({ cost_id: cost.cost_id, next: true }));
    if (loadCostFeed.fulfilled.match(result) && result.payload.cost) navigate(`/costs/feed/${result.payload.cost.cost_id}`);
  }
  if (!cost) return <section className="screen-message"><h1>{pending ? 'Загрузка ленты' : 'Издержка не найдена'}</h1><Link to="/costs">Вернуться к плитке</Link></section>;
  return <section className="feed-screen" aria-label="Лента издержек">
    <CostVideo key={cost.cost_id} url={costMediaUrl(cost.cost_video_url)} image={costMediaUrl(cost.cost_image_url)} />
    <div className="feed-shade" aria-hidden="true" />
    <div className="feed-copy"><h1>{cost.cost_name}</h1>
      <p className="feed-parameters">{cost.cost_behavior === 'fixed' ? 'Постоянные' : 'Переменные'} · Код {cost.cost_code}</p>
      <p className={expanded ? 'description-full' : 'description-preview'}>{cost.cost_description}</p>
      <Button className="description-toggle" aria-expanded={expanded} onClick={() => setExpanded(!expanded)}>{expanded ? 'Свернуть' : 'Ещё'}</Button>
    </div>
    <aside className="feed-actions" aria-label="Действия с карточкой">
      <Button className={`feed-action ${user && cost.is_liked ? 'cost-liked' : ''}`} disabled={!user}
        aria-label={user && cost.is_liked ? 'Убрать лайк' : 'Поставить лайк'} aria-pressed={!!user && cost.is_liked === 1}
        onClick={() => { void dispatch(changeCostLike({ id: cost.cost_id, liked: cost.is_liked ? 0 : 1 })); }}>
        <span className="feed-action__icon"><CostIcon name="heart" /></span><span className="feed-action__label">{cost.like_count}</span>
      </Button>
      <div className="parameter-disclosure">
        <Button className="feed-action" aria-label="Параметры издержки" aria-expanded={parameters} onClick={() => setParameters(!parameters)}><span className="feed-action__icon"><CostIcon name="parameters" /></span><span className="feed-action__label">Параметры</span></Button>
        {parameters && <div className="parameter-panel"><h2>Параметры</h2><dl>
          <div><dt>Вид издержек</dt><dd>{cost.cost_behavior === 'fixed' ? 'Постоянные' : 'Переменные'}</dd></div>
          <div><dt>Код издержки</dt><dd>{cost.cost_code}</dd></div>
        </dl></div>}
      </div>
      <Button className="feed-action" aria-label="Следующая издержка" onClick={() => { void next(); }}><span className="feed-action__icon"><CostIcon name="next" /></span><span className="feed-action__label">Далее</span></Button>
    </aside>
  </section>;
}
