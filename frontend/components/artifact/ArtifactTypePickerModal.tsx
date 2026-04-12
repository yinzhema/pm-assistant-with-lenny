'use client'

import { useEffect, useState } from 'react'
import { Trophy, Search, Bot, X, Loader2, Map, BarChart2, FileText, Globe, Briefcase } from 'lucide-react'
import { useAppStore } from '@/store/useAppStore'
import { startArtifactSession, getArtifactTypes } from '@/lib/api'
import type { ArtifactType, ArtifactTypeInfo } from '@/types'

const ICONS: Record<string, React.ReactNode> = {
  trophy: <Trophy className="h-5 w-5" />,
  search: <Search className="h-5 w-5" />,
  bot: <Bot className="h-5 w-5" />,
  map: <Map className="h-5 w-5" />,
  'bar-chart-2': <BarChart2 className="h-5 w-5" />,
  'file-text': <FileText className="h-5 w-5" />,
  globe: <Globe className="h-5 w-5" />,
  briefcase: <Briefcase className="h-5 w-5" />,
}

interface ArtifactTypePickerModalProps {
  onClose: () => void
}

export default function ArtifactTypePickerModal({ onClose }: ArtifactTypePickerModalProps) {
  const { sessionId, startArtifactSession: storeStart } = useAppStore()
  const [types, setTypes] = useState<ArtifactTypeInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [starting, setStarting] = useState<ArtifactType | null>(null)

  useEffect(() => {
    getArtifactTypes()
      .then((res) => setTypes(res.artifact_types as ArtifactTypeInfo[]))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleSelect = async (typeId: ArtifactType) => {
    if (starting) return
    setStarting(typeId)
    try {
      const res = await startArtifactSession(sessionId, typeId)
      storeStart(res.artifact_session_id, res.artifact_type, res.questions)
      onClose()
    } catch (err) {
      console.error('Failed to start artifact session', err)
      setStarting(null)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-2xl border border-zinc-700 bg-zinc-900 shadow-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 px-6 py-4">
          <div>
            <h2 className="text-base font-semibold text-zinc-100">Build an Artifact</h2>
            <p className="text-sm text-zinc-500 mt-0.5">Choose a type to get started</p>
          </div>
          <button
            onClick={onClose}
            className="rounded p-1 text-zinc-500 hover:text-zinc-300"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Type cards */}
        <div className="p-6 space-y-3 overflow-y-auto">
          {loading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-zinc-500" />
            </div>
          ) : (
            types.map((type) => (
              <button
                key={type.id}
                onClick={() => handleSelect(type.id)}
                disabled={!!starting}
                className="w-full flex items-start gap-4 rounded-xl border border-zinc-700 bg-zinc-800/50 p-4 text-left hover:border-blue-500/50 hover:bg-zinc-800 transition-colors disabled:opacity-60"
              >
                <div className="mt-0.5 text-blue-400">
                  {ICONS[type.icon] ?? <Search className="h-5 w-5" />}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-zinc-100">{type.title}</span>
                    <span className="text-xs text-zinc-500">{type.question_count} questions</span>
                    {starting === type.id && (
                      <Loader2 className="h-3.5 w-3.5 animate-spin text-blue-400" />
                    )}
                  </div>
                  <p className="text-sm text-zinc-400 mt-0.5 leading-snug">{type.description}</p>
                </div>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
