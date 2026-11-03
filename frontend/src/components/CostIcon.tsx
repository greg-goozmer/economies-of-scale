// Контурные иконки из шаблонов ЛР2. Вход добавлен для четвёртой вкладки ЛР5.
const paths = {
  feed: 'M5 5.5h14v13H5zM8 9h8M8 12h8M8 15h5',
  add: 'M12 5v14M5 12h14',
  tiles: 'M5 5h5v5H5zM14 5h5v5h-5zM5 14h5v5H5zM14 14h5v5h-5z',
  login: 'M14 4h6v16h-6M4 12h11M10 7l5 5-5 5',
  heart: 'M12 20s-7-4.35-7-10a4 4 0 0 1 7-2.65A4 4 0 0 1 19 10c0 5.65-7 10-7 10z',
  parameters: 'M4 7h8M16 7h4M4 17h2M10 17h10M14 4v6M8 14v6',
  next: 'M12 5v13M7 13l5 5 5-5',
};
export function CostIcon({ name }: { name: keyof typeof paths }) {
  return <svg viewBox="0 0 24 24" aria-hidden="true"><path d={paths[name]} /></svg>;
}
