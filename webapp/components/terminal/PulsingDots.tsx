interface PulsingDotsProps {
  size?: 'sm' | 'md';
}

export function PulsingDots({ size = 'sm' }: PulsingDotsProps) {
  const dotSize = size === 'sm' ? 'w-1.5 h-1.5' : 'w-2 h-2';
  return (
    <div className="flex gap-1">
      <span className={`${dotSize} bg-[#BB86FC] rounded-full animate-pulse`} style={{ animationDelay: '0ms' }}></span>
      <span className={`${dotSize} bg-[#BB86FC] rounded-full animate-pulse`} style={{ animationDelay: '150ms' }}></span>
      <span className={`${dotSize} bg-[#BB86FC] rounded-full animate-pulse`} style={{ animationDelay: '300ms' }}></span>
    </div>
  );
}
