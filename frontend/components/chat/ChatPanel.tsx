'use client'

import { useAppStore } from '@/store/useAppStore'
import ChatMessages from '@/components/chat/ChatMessages'
import ChatInput from '@/components/chat/ChatInput'
import EmptyState from '@/components/chat/EmptyState'
import TemplateOfferBanner from '@/components/chat/TemplateOfferBanner'

export default function ChatPanel() {
  const { hasMessages, offerTemplateId } = useAppStore()
  const hasAnyMessages = hasMessages()

  return (
    <div className="flex flex-col h-full relative">
      {/* Scrollable messages area */}
      <div className="flex-1 overflow-y-auto pb-32">
        {hasAnyMessages ? (
          <div className="px-4 py-4">
            <ChatMessages />
            {offerTemplateId && <TemplateOfferBanner />}
          </div>
        ) : (
          <EmptyState />
        )}
      </div>

      {/* Fixed input at bottom */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-surface via-surface to-transparent pt-6 pb-4 px-4">
        <ChatInput />
      </div>
    </div>
  )
}
