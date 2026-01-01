import { onMounted, onUnmounted } from 'vue';

export function usePolling(fn: () => void, interval: number) {
  let timer: any = null;

  const start = () => {
    if (timer) return;
    fn(); // Execute immediately
    timer = setInterval(fn, interval);
  };

  const stop = () => {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  };

  onMounted(() => {
    start();
  });

  onUnmounted(() => {
    stop();
  });

  return {
    start,
    stop,
  };
}
