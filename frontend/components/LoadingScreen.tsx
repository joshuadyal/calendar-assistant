import { Sparkles } from 'lucide-react';

export function LoadingScreen({
  label = 'Preparing your calendar',
}: {
  label?: string;
}) {
  return (
    <div className="loading-screen">
      <Sparkles size={18} /> {label}
    </div>
  );
}
