'use client'

import { useAppStore } from '@/store/useAppStore'
import PrdTranslationLayout from './PrdTranslationLayout'

export default function TranslationLayout() {
  const { translationMode, translationSession } = useAppStore()

  if (!translationMode || !translationSession) return null

  // Both prd-to-agent and idea-to-agent (when opened via prd route) use PrdTranslationLayout
  return <PrdTranslationLayout />
}
