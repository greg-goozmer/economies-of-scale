import { useState, type FormEvent } from 'react';
import { Alert, Button, Form } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { costError, costUsersApi } from '../api/costsClient';
import type { UserRead } from '../api/generated/CostsApi';
import { setCostAuthBusy, setCostUser, useCostsDispatch } from '../store/costsStore';

export function CostLoginPage() {
  const dispatch = useCostsDispatch();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [registration, setRegistration] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    setNotice('');
    dispatch(setCostAuthBusy(true));
    try {
      const response = await costUsersApi.post<UserRead>(registration ? '' : '/auth', { user_name: name.trim(), password });
      if (registration) {
        setRegistration(false);
        setNotice('Регистрация выполнена. Войдите с выбранным паролем.');
      } else {
        dispatch(setCostUser(response.data));
        navigate('/costs');
      }
    } catch (error) { setError(costError(error)); }
    finally { dispatch(setCostAuthBusy(false)); }
  }
  return <section className="cost-form-screen">
    <header className="screen-header"><p className="eyebrow">Масштаб</p><h1>{registration ? 'Регистрация' : 'Вход пользователя'}</h1></header>
    {error && <Alert variant="danger">{error}</Alert>}
    {notice && <Alert variant="success">{notice}</Alert>}
    <Form onSubmit={event => { void submit(event); }}>
      <Form.Group controlId="cost-user-name"><Form.Label>Имя пользователя</Form.Label><Form.Control required maxLength={50} autoComplete="username" value={name} onChange={event => setName(event.target.value)} /></Form.Group>
      <Form.Group controlId="cost-user-password"><Form.Label>Пароль</Form.Label><Form.Control required type="password" minLength={registration ? 8 : 1} maxLength={128} autoComplete={registration ? 'new-password' : 'current-password'} value={password} onChange={event => setPassword(event.target.value)} /></Form.Group>
      <Button type="submit" className="cost-primary">{registration ? 'Зарегистрироваться' : 'Войти'}</Button>
      <Button variant="link" className="cost-text-button" onClick={() => { setRegistration(!registration); setError(''); }}>{registration ? 'Уже есть учётная запись' : 'Создать учётную запись'}</Button>
    </Form>
  </section>;
}
