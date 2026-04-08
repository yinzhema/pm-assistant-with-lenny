'use client'

import { create } from 'zustand'
import { Message, Source } from '@/types'
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
}))
