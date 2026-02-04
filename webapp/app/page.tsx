'use client';

import { useEffect, useState } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';
import dynamic from 'next/dynamic';
import TitleBar from '@/components/terminal/TitleBar';
import TabBar from '@/components/terminal/TabBar';
import StatusBar from '@/components/terminal/StatusBar';
import { Storage } from '@/lib/storage';

// Dynamically import HybridTerminal with no SSR to avoid xterm.js server-side issues
const HybridTerminal = dynamic(
  () => import('@/components/terminal/HybridTerminal').then(mod => mod.default),
  { ssr: false }
);

export default function Home() {
  const { sessionId, setSessionId, setLoading } = useTerminalStore();
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

      {/* Terminal with inline visualizations */}
      <div className="flex-1 overflow-hidden">
        <HybridTerminal />
      </div>

      <StatusBar />
    </main>
  );
}
