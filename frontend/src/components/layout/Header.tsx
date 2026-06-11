// frontend/src/components/layout/Header.tsx

interface HeaderProps { title: string; subtitle?: string; action?: React.ReactNode }

export function Header({ title, subtitle, action }: HeaderProps) {
  return (
    <div className="flex items-center justify-between border-b border-white/8 px-8 py-5">
      <div>
        <h1 className="text-xl font-semibold text-white">{title}</h1>
        {subtitle && <p className="mt-0.5 text-sm text-slate-500">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}