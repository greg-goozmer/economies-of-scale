import { useEffect, useState, type FormEvent } from 'react';
import { Button, Form } from 'react-bootstrap';
import { Navigate, useNavigate } from 'react-router-dom';
import { CostImage, CostVideo } from '../components/CostMedia';
import { costMediaUrl } from '../api/costsClient';
import { createCostDraft, loadCostDraft, publishCostDraft, useCostsDispatch, useCostsSelector } from '../store/costsStore';

function useCostFilePreview(file: File | null) {
  const [url, setUrl] = useState('');
  useEffect(() => {
    if (!file) { setUrl(''); return; }
    const nextUrl = URL.createObjectURL(file);
    setUrl(nextUrl);
    return () => URL.revokeObjectURL(nextUrl);
  }, [file]);
  return url;
}

export function CostDraftPage() {
  const dispatch = useCostsDispatch();
  const navigate = useNavigate();
  const { user, draft } = useCostsSelector(state => state.costs);
  const [loaded, setLoaded] = useState(false);
  const [name, setName] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [video, setVideo] = useState<File | null>(null);
  const [description, setDescription] = useState('');
  const [behavior, setBehavior] = useState<'fixed' | 'variable'>('fixed');
  const [code, setCode] = useState('');
  const imagePreview = useCostFilePreview(image);
  const videoPreview = useCostFilePreview(video);
  useEffect(() => {
    if (!user) return;
    void dispatch(loadCostDraft()).then(result => {
      setLoaded(loadCostDraft.fulfilled.match(result));
    });
  }, [dispatch, user]);
  useEffect(() => {
    setDescription(draft?.cost_description || '');
    setBehavior(draft?.cost_behavior === 'variable' ? 'variable' : 'fixed');
    setCode(draft?.cost_code == null ? '' : String(draft.cost_code));
  }, [draft]);
  if (!user) return <Navigate to="/costs/login" replace />;
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (draft) {
      const result = await dispatch(publishCostDraft({ id: draft.cost_id, data: {
        cost_description: description.trim(), cost_behavior: behavior, cost_code: Number(code),
      } }));
      if (publishCostDraft.fulfilled.match(result)) navigate('/costs');
    } else if (image && video) {
      const result = await dispatch(createCostDraft({ cost_name: name.trim(), image, video }));
      if (createCostDraft.rejected.match(result)) void dispatch(loadCostDraft());
    }
  }
  return <section className="cost-form-screen">
    <header className="screen-header"><p className="eyebrow">{user.user_name}</p><h1>{draft ? 'Публикация издержки' : 'Добавление издержки'}</h1></header>
    {!loaded ? <Button className="cost-primary" onClick={() => { void dispatch(loadCostDraft()).then(result => setLoaded(loadCostDraft.fulfilled.match(result))); }}>Загрузить черновик</Button> :
      <Form onSubmit={event => { void submit(event); }}>
        {draft ? <>
          <h2 className="cost-draft-name">{draft.cost_name}</h2>
          <div className="cost-draft-image"><CostImage url={costMediaUrl(draft.cost_image_url)} name={draft.cost_name} /></div>
          <Form.Group controlId="cost-description"><Form.Label>Описание издержки</Form.Label><Form.Control as="textarea" rows={3} required maxLength={500} value={description} onChange={event => setDescription(event.target.value)} /></Form.Group>
          <Form.Group controlId="cost-behavior"><Form.Label>Тип издержки</Form.Label><Form.Select value={behavior} onChange={event => setBehavior(event.target.value as 'fixed' | 'variable')}><option value="fixed">Постоянные</option><option value="variable">Переменные</option></Form.Select></Form.Group>
          <Form.Group controlId="cost-code"><Form.Label>Код издержки</Form.Label><Form.Control type="number" min={0} step={1} required value={code} onChange={event => setCode(event.target.value)} /></Form.Group>
          <Button type="submit" className="cost-primary" disabled={!description.trim() || code === '' || !Number.isInteger(Number(code)) || Number(code) < 0}>Опубликовать</Button>
        </> : <>
          <Form.Group controlId="cost-name"><Form.Label>Название издержки</Form.Label><Form.Control required maxLength={100} value={name} onChange={event => setName(event.target.value)} /></Form.Group>
          <Form.Group controlId="cost-image"><Form.Label>Изображение</Form.Label><Form.Control required type="file" accept="image/*" onChange={event => setImage((event.target as HTMLInputElement).files?.[0] || null)} /></Form.Group>
          <Form.Group controlId="cost-video"><Form.Label>Видео</Form.Label><Form.Control required type="file" accept="video/mp4,video/webm" onChange={event => setVideo((event.target as HTMLInputElement).files?.[0] || null)} /></Form.Group>
          {(image || video) && <div className="cost-file-preview"><CostVideo url={videoPreview} image={imagePreview} /></div>}
          <Button type="submit" className="cost-primary" disabled={!name.trim() || !image || !video}>Далее</Button>
        </>}
      </Form>}
  </section>;
}
