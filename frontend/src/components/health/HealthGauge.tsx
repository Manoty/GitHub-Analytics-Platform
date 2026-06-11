// frontend/src/components/health/HealthGauge.tsx

interface Props { score: number }

export function HealthGauge({ score }: Props) {
  const clamped = Math.min(Math.max(score, 0), 100);
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (clamped / 100) * circumference;

  const color =
    clamped >= 80 ? "#34d399" :
    clamped >= 60 ? "#60a5fa" :
    clamped >= 40 ? "#fbbf24" : "#f87171";

  return (
    <div className="relative flex items-center justify-center">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r="54" fill="none" stroke="#ffffff08" strokeWidth="12" />
        <circle
          cx="70" cy="70" r="54"
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 70 70)"
          style={{ transition: "stroke-dashoffset 0.8s ease" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold text-white">{clamped.toFixed(0)}</span>
        <span className="text-xs text-slate-500">/ 100</span>
      </div>
    </div>
  );
}