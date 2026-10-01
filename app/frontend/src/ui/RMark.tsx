// 品牌字标：衬线体 T（旧版是 Feather 风格的 R，与左上角品牌不符）。
// 必须保持恰好 3 条 path —— app.css / studio.css 的入场与运行态动画
// 都按 path:nth-child(1..3) 编排（横笔 → 竖笔 → 底衬线，依次描画）。
// 造型不是光秃秃的 T：横笔两端带下弯的括弧衬线、竖笔落地带短衬线，
// 远看是一枚有笔锋的衬线 T，而不是三根棍。
export function RMark({ className = "rmark" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 16 16" aria-hidden="true">
      <path pathLength={100} d="M3.1 5.3V3.5h9.8v1.8" />
      <path pathLength={100} d="M8 3.5v9.9" />
      <path pathLength={100} d="M6.2 13.4h3.6" />
    </svg>
  );
}
