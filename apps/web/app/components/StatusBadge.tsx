const statusStyles: Record<string, string> = {
  pending: "border-amber-200 bg-amber-50 text-amber-700",
  running: "border-blue-200 bg-blue-50 text-blue-700",
  succeeded: "border-emerald-200 bg-emerald-50 text-emerald-700",
  failed: "border-red-200 bg-red-50 text-red-700"
};

const statusLabels: Record<string, string> = {
  pending: "排队中",
  running: "生成中",
  succeeded: "已完成",
  failed: "失败"
};

export function StatusBadge({ status }: { status: string }) {
  const style = statusStyles[status] ?? "border-slate-200 bg-slate-100 text-slate-700";
  const label = statusLabels[status] ?? status;

  return (
    <span className={`inline-flex items-center rounded border px-2.5 py-1 text-xs font-medium ${style}`}>
      {label}
    </span>
  );
}
