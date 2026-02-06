'use client';

import { useEffect, useState } from 'react';
import { useTerminalStore } from '@/store/useTerminalStore';
import dynamic from 'next/dynamic';
import TitleBar from '@/components/terminal/TitleBar';
import TabBar from '@/components/terminal/TabBar';
import { Storage } from '@/utils/storage';

// Dynamically import HybridTerminal with no SSR to avoid xterm.js server-side issues
const HybridTerminal = dynamic(
  () => import('@/components/terminal/HybridTerminal').then(mod => mod.default),
  { ssr: false }
);

export default function Home() {
  const { sessionId, setSessionId } = useTerminalStore();
  const [mounted, setMounted] = useState(false);

  // Wait for client-side mount to avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
    if (!sessionId) {
      Storage.getOrCreateSession().then(setSessionId).catch(console.error);
    }
  }, [sessionId, setSessionId]);

  // During SSR or before mount, show minimal loading state
  if (!mounted) {
    return (
      <main className="h-screen flex flex-col bg-[#1E1E1E] overflow-hidden">
        <div className="flex-1 flex items-center justify-center">
          <div className="text-[#5C6AC4]">Initializing TermAI Explorer...</div>
        </div>
      </main>
    );
  }

  // After mount, render full app
  return (
    <main className="h-screen flex flex-col bg-[#1E1E1E] overflow-hidden">
      {!sessionId ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-[#5C6AC4]">Initializing TermAI Explorer...</div>
        </div>
      ) : (
        <>
          {/* TitleBar and TabBar */}
          <TitleBar />
          <TabBar />

          {/* Terminal with inline visualizations */}
          <div className="flex-1 overflow-hidden">
            <HybridTerminal />
          </div>
        </>
      )}
    </main>
  );
}
