'use client'

import { useState, useRef } from 'react'
import { Upload, FileText, Loader2 } from 'lucide-react'

interface PrdUploadPanelProps {
  onSubmit: (prdText: string) => void
  isLoading: boolean
}

export default function PrdUploadPanel({ onSubmit, isLoading }: PrdUploadPanelProps) {
  const [prdText, setPrdText] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const text = await file.text()
    setPrdText(text)
  }

  return (
    <div className="flex flex-col gap-4 p-6 h-full">
      <div>
        <h2 className="text-base font-semibold text-zinc-100">Translate PRD → agent.md</h2>
        <p className="text-sm text-zinc-500 mt-1">
          Paste your PRD below or upload a .md / .txt file. AskProduct will extract structure,
          generate an agent.md, and identify gaps.
        </p>
      </div>

      <textarea
        value={prdText}
        onChange={(e) => setPrdText(e.target.value)}
        placeholder="Paste your PRD here…"
        className="flex-1 resize-none rounded-lg border border-zinc-700 bg-zinc-800/60 px-4 py-3 text-sm text-zinc-100 placeholder:text-zinc-600 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        rows={16}
      />

      <div className="flex items-center gap-3">
        <button
          onClick={() => fileRef.current?.click()}
          className="flex items-center gap-1.5 rounded-lg border border-zinc-700 px-3 py-2 text-sm text-zinc-400 hover:border-zinc-600 hover:text-zinc-200 transition-colors"
        >
          <Upload className="h-4 w-4" />
          Upload file
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".md,.txt,.doc,.docx"
          className="hidden"
          onChange={handleFileChange}
        />

        <span className="text-xs text-zinc-600">.md, .txt, .docx supported</span>

        <button
          onClick={() => onSubmit(prdText)}
          disabled={!prdText.trim() || isLoading}
          className="ml-auto flex items-center gap-1.5 rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Processing…
            </>
          ) : (
            <>
              <FileText className="h-4 w-4" />
              Translate PRD
            </>
          )}
        </button>
      </div>

      <p className="text-xs text-zinc-600">
        Processing uses the frontier model and takes ~20–30 seconds for a full PRD.
      </p>
    </div>
  )
}
