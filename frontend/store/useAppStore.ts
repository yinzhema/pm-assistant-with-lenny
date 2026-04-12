'use client'

import { create } from 'zustand'
import {
  Message,
  Source,
  ArtifactSession,
  ArtifactSectionPreview,
  ArtifactType,
  Question,
  TranslationSession,
  TranslationMode,
  AgentMdSection,
  GapItem,
} from '@/types'
import { generateId } from '@/lib/utils'

const SESSION_STORAGE_KEY = 'askproduct_session_id'

function getOrCreateSessionId(): string {
  if (typeof window === 'undefined') return generateId()
  const existing = localStorage.getItem(SESSION_STORAGE_KEY)
  if (existing) return existing
  const newId = generateId()
  localStorage.setItem(SESSION_STORAGE_KEY, newId)
  return newId
}

interface AppState {
  // Chat
  messages: Message[]
  isStreaming: boolean
  streamingContent: string

  // Template offer
  offerTemplateId: string | null
  offerTemplateName: string | null

  // Document / workspace
  documentHtml: string
  documentTitle: string
  documentId: string | null
  templateId: string | null

  // UI
  showFeedback: boolean
  sessionId: string

  // Computed
  workspaceActive: () => boolean
  hasMessages: () => boolean

  // Actions
  addUserMessage: (content: string) => void
  appendStreamToken: (token: string) => void
  finalizeAssistantMessage: (sources: Source[]) => void
  setOfferTemplate: (id: string, name: string) => void
  clearOfferTemplate: () => void
  openDocument: (html: string, templateId: string, title: string) => void
  updateDocumentHtml: (html: string) => void
  updateDocumentTitle: (title: string) => void
  setDocumentId: (id: string) => void
  closeDocument: () => void
  newChat: () => void
  setShowFeedback: (v: boolean) => void

  // ── Artifact Builder slice ────────────────────────────────────────────────
  artifactMode: 'builder' | null
  artifactSession: ArtifactSession | null
  artifactSectionPreviews: Record<string, ArtifactSectionPreview>

  startArtifactSession: (
    id: string,
    artifactType: ArtifactType,
    questions: Question[]
  ) => void
  setArtifactSectionStreaming: (sectionKey: string, streaming: boolean) => void
  appendArtifactSectionChunk: (sectionKey: string, chunk: string) => void
  markArtifactSectionAnswered: (sectionKey: string) => void
  markArtifactSectionSkipped: (sectionKey: string) => void
  setArtifactAnswer: (questionId: string, answer: string) => void
  setArtifactCurrentIndex: (index: number) => void
  closeArtifactBuilder: () => void

  // ── Translation slice ─────────────────────────────────────────────────────
  translationMode: TranslationMode | null
  translationSession: TranslationSession | null

  startTranslationSession: (
    id: string,
    mode: TranslationMode,
    prdText: string
  ) => void
  addAgentSection: (section: AgentMdSection) => void
  updateAgentSection: (sectionKey: string, html: string, confidence: AgentMdSection['confidence']) => void
  setTranslationGaps: (gaps: GapItem[]) => void
  addTranslationClarification: (questionId: string, answer: string) => void
  setTranslationStatus: (status: TranslationSession['status']) => void
  closeTranslation: () => void
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  messages: [],
  isStreaming: false,
  streamingContent: '',

  offerTemplateId: null,
  offerTemplateName: null,

  documentHtml: '',
  documentTitle: 'Untitled',
  documentId: null,
  templateId: null,

  showFeedback: false,
  sessionId: getOrCreateSessionId(),

  // Computed
  workspaceActive: () => get().documentHtml.length > 0,
  hasMessages: () => get().messages.length > 0,

  // Actions
  addUserMessage: (content: string) => {
    const message: Message = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    }
    set((state) => ({
      messages: [...state.messages, message],
      isStreaming: true,
      streamingContent: '',
    }))
  },

  appendStreamToken: (token: string) => {
    set((state) => ({
      streamingContent: state.streamingContent + token,
    }))
  },

  finalizeAssistantMessage: (sources: Source[]) => {
    const { streamingContent } = get()
    if (!streamingContent.trim()) {
      set({ isStreaming: false, streamingContent: '' })
      return
    }
    const message: Message = {
      id: generateId(),
      role: 'assistant',
      content: streamingContent,
      sources,
      timestamp: new Date().toISOString(),
    }
    set((state) => ({
      messages: [...state.messages, message],
      isStreaming: false,
      streamingContent: '',
    }))
  },

  setOfferTemplate: (id: string, name: string) => {
    set({ offerTemplateId: id, offerTemplateName: name })
  },

  clearOfferTemplate: () => {
    set({ offerTemplateId: null, offerTemplateName: null })
  },

  openDocument: (html: string, templateId: string, title: string) => {
    set({
      documentHtml: html,
      templateId,
      documentTitle: title,
      documentId: null,
      offerTemplateId: null,
      offerTemplateName: null,
    })
  },

  updateDocumentHtml: (html: string) => {
    set({ documentHtml: html })
  },

  updateDocumentTitle: (title: string) => {
    set({ documentTitle: title })
  },

  setDocumentId: (id: string) => {
    set({ documentId: id })
  },

  closeDocument: () => {
    set({
      documentHtml: '',
      documentTitle: 'Untitled',
      documentId: null,
      templateId: null,
    })
  },

  newChat: () => {
    set({
      messages: [],
      isStreaming: false,
      streamingContent: '',
      offerTemplateId: null,
      offerTemplateName: null,
      documentHtml: '',
      documentTitle: 'Untitled',
      documentId: null,
      templateId: null,
      showFeedback: false,
    })
  },

  setShowFeedback: (v: boolean) => {
    set({ showFeedback: v })
  },

  // ── Artifact Builder ────────────────────────────────────────────────────────
  artifactMode: null,
  artifactSession: null,
  artifactSectionPreviews: {},

  startArtifactSession: (id, artifactType, questions) => {
    const previews: Record<string, ArtifactSectionPreview> = {}
    for (const q of questions) {
      previews[q.section_key] = {
        sectionKey: q.section_key,
        sectionLabel: q.section_label,
        placeholder: q.placeholder,
        html: '',
        isStreaming: false,
        isAnswered: false,
        isSkipped: false,
      }
    }
    set({
      artifactMode: 'builder',
      artifactSession: {
        id,
        artifactType,
        questions,
        currentIndex: 0,
        answers: {},
        skipped: [],
        status: 'in_progress',
      },
      artifactSectionPreviews: previews,
    })
  },

  setArtifactSectionStreaming: (sectionKey, streaming) => {
    set((state) => ({
      artifactSectionPreviews: {
        ...state.artifactSectionPreviews,
        [sectionKey]: {
          ...state.artifactSectionPreviews[sectionKey],
          html: streaming ? '' : state.artifactSectionPreviews[sectionKey]?.html ?? '',
          isStreaming: streaming,
        },
      },
    }))
  },

  appendArtifactSectionChunk: (sectionKey, chunk) => {
    set((state) => {
      const prev = state.artifactSectionPreviews[sectionKey]
      if (!prev) return {}
      return {
        artifactSectionPreviews: {
          ...state.artifactSectionPreviews,
          [sectionKey]: { ...prev, html: prev.html + chunk, isStreaming: true },
        },
      }
    })
  },

  markArtifactSectionAnswered: (sectionKey) => {
    set((state) => ({
      artifactSectionPreviews: {
        ...state.artifactSectionPreviews,
        [sectionKey]: {
          ...state.artifactSectionPreviews[sectionKey],
          isAnswered: true,
          isStreaming: false,
          isSkipped: false,
        },
      },
    }))
  },

  markArtifactSectionSkipped: (sectionKey) => {
    set((state) => ({
      artifactSectionPreviews: {
        ...state.artifactSectionPreviews,
        [sectionKey]: {
          ...state.artifactSectionPreviews[sectionKey],
          isSkipped: true,
          isStreaming: false,
          isAnswered: false,
        },
      },
    }))
  },

  setArtifactAnswer: (questionId, answer) => {
    set((state) => {
      if (!state.artifactSession) return {}
      return {
        artifactSession: {
          ...state.artifactSession,
          answers: { ...state.artifactSession.answers, [questionId]: answer },
          currentIndex: Math.min(
            state.artifactSession.currentIndex + 1,
            state.artifactSession.questions.length - 1
          ),
        },
      }
    })
  },

  setArtifactCurrentIndex: (index) => {
    set((state) => {
      if (!state.artifactSession) return {}
      return {
        artifactSession: { ...state.artifactSession, currentIndex: index },
      }
    })
  },

  closeArtifactBuilder: () => {
    set({ artifactMode: null, artifactSession: null, artifactSectionPreviews: {} })
  },

  // ── Translation ─────────────────────────────────────────────────────────────
  translationMode: null,
  translationSession: null,

  startTranslationSession: (id, mode, prdText) => {
    set({
      translationMode: mode,
      translationSession: {
        id,
        translationMode: mode,
        prdText,
        agentSections: [],
        gaps: [],
        clarifications: {},
        status: 'extracting',
      },
    })
  },

  addAgentSection: (section) => {
    set((state) => {
      if (!state.translationSession) return {}
      return {
        translationSession: {
          ...state.translationSession,
          agentSections: [...state.translationSession.agentSections, section],
        },
      }
    })
  },

  updateAgentSection: (sectionKey, html, confidence) => {
    set((state) => {
      if (!state.translationSession) return {}
      const sections = state.translationSession.agentSections.map((s) =>
        s.section_key === sectionKey ? { ...s, html, confidence } : s
      )
      if (!sections.find((s) => s.section_key === sectionKey)) {
        sections.push({ section_key: sectionKey, html, confidence })
      }
      return {
        translationSession: { ...state.translationSession, agentSections: sections },
      }
    })
  },

  setTranslationGaps: (gaps) => {
    set((state) => {
      if (!state.translationSession) return {}
      return {
        translationSession: { ...state.translationSession, gaps },
      }
    })
  },

  addTranslationClarification: (questionId, answer) => {
    set((state) => {
      if (!state.translationSession) return {}
      return {
        translationSession: {
          ...state.translationSession,
          clarifications: {
            ...state.translationSession.clarifications,
            [questionId]: answer,
          },
        },
      }
    })
  },

  setTranslationStatus: (status) => {
    set((state) => {
      if (!state.translationSession) return {}
      return {
        translationSession: { ...state.translationSession, status },
      }
    })
  },

  closeTranslation: () => {
    set({ translationMode: null, translationSession: null })
  },
}))
