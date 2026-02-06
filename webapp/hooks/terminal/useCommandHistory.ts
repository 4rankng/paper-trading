import { useState, useCallback } from 'react';

export function useCommandHistory(commandHistory: string[]) {
  const [historyIndex, setHistoryIndex] = useState(-1);

  const navigateUp = useCallback(() => {
    if (historyIndex < commandHistory.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      const cmdIndex = commandHistory.length - 1 - newIndex;
      return commandHistory[cmdIndex] || '';
    }
    return null;
  }, [historyIndex, commandHistory]);

  const navigateDown = useCallback(() => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      const cmdIndex = commandHistory.length - 1 - newIndex;
      return commandHistory[cmdIndex] || '';
    } else if (historyIndex === 0) {
      setHistoryIndex(-1);
      return '';
    }
    return null;
  }, [historyIndex, commandHistory]);

  const resetIndex = useCallback(() => {
    setHistoryIndex(-1);
  }, []);

  return {
    historyIndex,
    navigateUp,
    navigateDown,
    resetIndex,
  };
}
