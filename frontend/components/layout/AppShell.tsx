'use client'

import { useAppStore } from '@/store/useAppStore'
import TopBar from '@/components/layout/TopBar'
import ChatPanel from '@/components/chat/ChatPanel'
import CanvasPanel from '@/components/canvas/CanvasPanel'
import FeedbackModal from '@/components/feedback/FeedbackModal'
import ArtifactBuilderPanel from '@/components/artifact/ArtifactBuilderPanel'
import TranslationLayout from '@/components/translation/TranslationLayout'

export default function AppShell() {
  const { workspaceActive, showFeedback, artifactMode, translationMode } = useAppStore()
  const isWorkspace = workspaceActive()

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-surface">
      <TopBar />
      <main className="flex flex-1 overflow-hidden pt-14">
        {artifactMode === 'builder' ? (
          <BuilderLayout />
        ) : translationMode ? (
          <TranslationLayout />
        ) : isWorkspace ? (
          <SplitLayout />
        ) : (
          <SingleColumn />
        )}
      </main>
      {showFeedback && <FeedbackModal />}
    </div>
  )
}

function BuilderLayout() {
  return (
    <div className="flex w-full h-full overflow-hidden bg-zinc-950">
      <ArtifactBuilderPanel />
    </div>
  )
}

function SplitLayout() {
  return (
    <div className="flex w-full h-full overflow-hidden">
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <ChatPanel />
      </div>
      <div className="flex flex-col w-1/2 min-w-0 overflow-hidden canvas-panel">
        <CanvasPanel />
      </div>
    </div>
  )
}

function SingleColumn() {
  return (
    <div className="flex flex-col w-full max-w-3xl mx-auto px-4 overflow-hidden">
      <ChatPanel />
    </div>
  )
}
