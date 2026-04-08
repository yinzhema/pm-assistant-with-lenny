'use client'

import { useState } from 'react'
import { BubbleMenu, Editor } from '@tiptap/react'
import { useAppStore } from '@/store/useAppStore'
import { improveSelection } from '@/lib/api'

interface Props {
  editor: Editor
}

type AIAction = 'improve' | 'expand' | 'critique' | 'simplify'

const ACTIONS: { id: AIAction; label: string }[] = [
  { id: 'improve', label: '✨ Improve' },
  { id: 'expand', label: '📝 Expand' },
  { id: 'critique', label: '🔍 Critique' },
  { id: 'simplify', label: '✂️ Simplify' },
]

export default function BubbleMenuAI({ editor }: Props) {
  const [activeAction, setActiveAction] = useState<AIAction | null>(null)
  const { documentHtml } = useAppStore()

  async function handleAction(action: AIAction) {
    if (activeAction) return

    const { from, to } = editor.state.selection
    if (from === to) return

    const selectedText = editor.state.doc.textBetween(from, to, ' ')
    if (!selectedText.trim()) return

    setActiveAction(action)
    try {
      const result = await improveSelection({
        action,
        selected_text: selectedText,
        full_html: documentHtml,
      })

      // Replace the selected text with the improved HTML
      editor
        .chain()
        .focus()
        .deleteRange({ from, to })
        .insertContentAt(from, result.html)
        .run()
    } catch (err) {
      console.error('AI action failed:', err)
    } finally {
      setActiveAction(null)
    }
  }

  return (
    <BubbleMenu
      editor={editor}
      tippyOptions={{ duration: 150, placement: 'top' }}
      shouldShow={({ editor: ed }) => {
        const { from, to } = ed.state.selection
        return from !== to
      }}
    >
      <div className="bubble-menu-ai">
        {ACTIONS.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => handleAction(id)}
            disabled={activeAction !== null}
            title={`${label} selected text`}
          >
            {activeAction === id ? '…' : label}
          </button>
        ))}
      </div>
    </BubbleMenu>
  )
}
