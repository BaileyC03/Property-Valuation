import { useState, useEffect, useRef } from 'react';

function easeOutExpo(t: number): number {
  return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
}

export function useCountUp(
  end: number,
  duration: number = 1500,
  startOnMount: boolean = true
): number {
  const [value, setValue] = useState(0);
  const prevEnd = useRef(0);
  const frameRef = useRef<number>(0);

  useEffect(() => {
    if (!startOnMount) return;

    const startValue = prevEnd.current;
    const startTime = performance.now();

    const tick = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easeOutExpo(progress);

      setValue(Math.round(startValue + (end - startValue) * easedProgress));

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(tick);
      } else {
        prevEnd.current = end;
      }
    };

    frameRef.current = requestAnimationFrame(tick);

    return () => cancelAnimationFrame(frameRef.current);
  }, [end, duration, startOnMount]);

  return value;
}

export function formatGBP(value: number): string {
  return new Intl.NumberFormat('en-GB', {
    style: 'currency',
    currency: 'GBP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}
