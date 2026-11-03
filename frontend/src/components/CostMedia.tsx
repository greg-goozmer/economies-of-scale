import { useState } from 'react';

export const DEFAULT_COST_IMAGE = '/media/default-cost.svg';
export const DEFAULT_COST_VIDEO = '/media/default-cost.mp4';

export function CostImage({ url, name }: { url: string; name: string }) {
  const [failed, setFailed] = useState(false);
  return <img src={!url || failed ? DEFAULT_COST_IMAGE : url} alt={name}
    onError={() => setFailed(true)} className="cost-image" />;
}

export function CostVideo({ url, image }: { url: string; image: string }) {
  const [failed, setFailed] = useState(false);
  return <video src={!url || failed ? DEFAULT_COST_VIDEO : url}
    poster={image || DEFAULT_COST_IMAGE} onError={() => { if (!failed) setFailed(true); }}
    className="cost-video" autoPlay muted loop playsInline aria-label="Видео издержки" />;
}
