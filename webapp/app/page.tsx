'use client';

import { useEffect, useState } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';
import dynamic from 'next/dynamic';
import TitleBar from '@/components/terminal/TitleBar';
import TabBar from '@/components/terminal/TabBar';
import StatusBar from '@/components/terminal/StatusBar';
import VizPanel from '@/components/terminal/VizPanel';
import { Storage } from '@/lib/storage';

// Dynamically import XtermTerminal with no SSR to avoid xterm.js server-side issues
const XtermTerminal = dynamic(
  () => import('@/components/terminal/XtermTerminal').then(mod => mod.default),
  { ssr: false }
);

export default function Home() {
  const { sessionId, setSessionId, setLoading, visualizations, addVisualization } = useTerminalStore();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const initSession = async () => {
      setLoading(true);
      try {
        const id = await Storage.getOrCreateSession();
        setSessionId(id);
      } catch (error) {
        console.error('Failed to initialize session:', error);
      } finally {
        setLoading(false);
        setIsInitialized(true);
      }
    };

    if (!sessionId) {
      initSession();
    } else {
      setIsInitialized(true);
    }
  }, [sessionId, setSessionId, setLoading]);

  if (!isInitialized) {
    return (
      <div className="h-screen bg-[#1E1E1E] flex items-center justify-center">
        <div className="text-[#5C6AC4]">Initializing TermAI Explorer...</div>
      </div>
    );
  }

  return (
    <main className="h-screen flex flex-col bg-[#1E1E1E] overflow-hidden">
      <TitleBar />
      <TabBar />

      <div className="flex-1 flex overflow-hidden">
        {/* Terminal area */}
        <div className="flex-1 overflow-hidden">
          <XtermTerminal
            onVisualization={(viz) => addVisualization(viz)}
          />
        </div>

        {/* Visualization panel */}
        <VizPanel visualizations={visualizations} />
      </div>

      <StatusBar />
    </main>
  );
}
