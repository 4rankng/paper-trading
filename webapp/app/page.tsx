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

  // Initialize session synchronously on mount - localStorage is instant
  useEffect(() => {
    if (!sessionId) {
      Storage.getOrCreateSession().then(setSessionId).catch(console.error);
    }
  }, [sessionId, setSessionId]);

  // Only show loading briefly on first visit (no sessionId yet)
  if (!sessionId) {
    return (
      <div className="h-screen bg-[#1E1E1E] flex items-center justify-center">
        <div className="text-[#5C6AC4]">Initializing TermAI Explorer...</div>
      </div>
    );
  }

  return (
    <main className="h-screen flex flex-col bg-[#1E1E1E] overflow-hidden">
      {/* TitleBar and TabBar */}
      <TitleBar />
      <TabBar />

      {/* Terminal with inline visualizations */}
      <div className="flex-1 overflow-hidden">
        <HybridTerminal />
      </div>
    </main>
  );
}
