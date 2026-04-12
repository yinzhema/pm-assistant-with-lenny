'use client'

import { useAppStore } from '@/store/useAppStore'
import { useArtifactStream } from '@/hooks/useArtifactStream'
import ArtifactProgressBar from './ArtifactProgressBar'
import QuestionCard from './QuestionCard'
import ArtifactLivePreview from './ArtifactLivePreview'
import ArtifactBuilderToolbar from './ArtifactBuilderToolbar'

export default function ArtifactBuilderPanel() {
  const {
    artifactSession,
    artifactSectionPreviews,
    closeArtifactBuilder,
    openDocument,
  } = useAppStore()

  const {
    sendAnswer,
    skipQuestion,
    jumpToQuestion,
    synthesize,
    isStreaming,
    isSynthesizing,
    kbSnippets,
  } = useArtifactStream()

  if (!artifactSession) return null

  const { questions, currentIndex } = artifactSession
  const currentQuestion = questions[currentIndex]

  // "All answered" = every question has either an answer or is skipped
  const totalResponded =
    Object.keys(artifactSession.answers).length + artifactSession.skipped.length
  const allAnswered = totalResponded >= questions.length

  const handleSynthesize = () => {
    synthesize((html, title) => {
      closeArtifactBuilder()
      openDocument(html, artifactSession.artifactType, title)
    })
  }

  // Find artifact type display name from tree title via question metadata
  const title = (() => {
    const typeMap: Record<string, string> = {
      'play-to-win': 'Play to Win',
      'opportunity-assessment': 'Opportunity Assessment',
      'idea-to-agent': 'Idea → agent.md',
    }
    return typeMap[artifactSession.artifactType] ?? artifactSession.artifactType
  })()

  return (
    <div className="flex h-full overflow-hidden">
      {/* Left: Q&A panel */}
      <div className="flex w-[42%] shrink-0 flex-col border-r border-zinc-800 overflow-hidden">
        <ArtifactBuilderToolbar
          title={title}
          allAnswered={allAnswered}
          isSynthesizing={isSynthesizing}
          onSynthesize={handleSynthesize}
          onClose={closeArtifactBuilder}
        />

        <ArtifactProgressBar
          current={currentIndex}
          total={questions.length}
          title={title}
        />

        <div className="flex-1 overflow-y-auto">
          {currentQuestion && !allAnswered && (
            <QuestionCard
              question={currentQuestion}
              kbSnippet={kbSnippets[currentQuestion.id] ?? null}
              onSubmit={(answer) => sendAnswer(currentQuestion.id, answer)}
              onSkip={() => skipQuestion(currentQuestion.id)}
              isStreaming={isStreaming}
            />
          )}

          {allAnswered && !isSynthesizing && (
            <div className="px-6 py-8 text-center">
              <p className="text-sm text-zinc-400 mb-4">
                All questions answered. Click <strong className="text-zinc-200">Synthesize &amp; Finish</strong> above to generate your complete artifact using the frontier model.
              </p>
            </div>
          )}

          {isSynthesizing && (
            <div className="px-6 py-8 text-center">
              <div className="inline-flex items-center gap-2 text-sm text-blue-400">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-blue-400 border-t-transparent" />
                Synthesizing full artifact…
              </div>
              <p className="text-xs text-zinc-500 mt-2">This uses the frontier model for maximum quality.</p>
            </div>
          )}

          {/* Answered questions summary */}
          {Object.keys(artifactSession.answers).length > 0 && (
            <div className="border-t border-zinc-800 px-6 py-4">
              <p className="text-xs font-semibold uppercase tracking-widest text-zinc-600 mb-3">Answered</p>
              <div className="space-y-2">
                {questions
                  .filter((q) => artifactSession.answers[q.id])
                  .map((q) => (
                    <button
                      key={q.id}
                      onClick={() => jumpToQuestion(q.id)}
                      className="w-full text-left rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 hover:border-zinc-700 transition-colors"
                    >
                      <p className="text-xs text-zinc-500 truncate">{q.section_label}</p>
                      <p className="text-xs text-zinc-400 truncate mt-0.5">
                        {artifactSession.answers[q.id]}
                      </p>
                    </button>
                  ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right: Live preview */}
      <div className="flex-1 overflow-hidden">
        <ArtifactLivePreview
          session={artifactSession}
          previews={artifactSectionPreviews}
          onSectionClick={jumpToQuestion}
        />
      </div>
    </div>
  )
}
