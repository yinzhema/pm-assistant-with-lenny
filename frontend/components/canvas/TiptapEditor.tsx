'use client'

import { useEffect, useRef } from 'react'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import Placeholder from '@tiptap/extension-placeholder'
import { useAppStore } from '@/store/useAppStore'

const DEBOUNCE_MS = 500

export default function TiptapEditor() {
  const { documentHtml, updateDocumentHtml } = useAppStore()
  const debounceTimer = useRef<NodeJS.Timeout | null>(null)
  const isExternalUpdate = useRef(false)

  const editor = useEditor({
    extensions: [
      StarterKit,
      Table.configure({ resizable: true }),
      TableRow,
      TableCell,
      TableHeader,
      Placeholder.configure({
        placeholder: 'Start writing your document…',
      }),
    ],
    content: documentHtml || '',
    editorProps: {
      attributes: {
        class: 'tiptap-editor',
        spellcheck: 'true',
      },
    },
    onUpdate: ({ editor: ed }) => {
      if (isExternalUpdate.current) return
      const html = ed.getHTML()
      if (debounceTimer.current) clearTimeout(debounceTimer.current)
      debounceTimer.current = setTimeout(() => {
        updateDocumentHtml(html)
      }, DEBOUNCE_MS)
    },
  })

  // Sync external HTML changes (e.g. from AI generation or version restore)
  useEffect(() => {
    if (!editor) return
    const currentHtml = editor.getHTML()
    if (documentHtml !== currentHtml) {
      isExternalUpdate.current = true
      editor.commands.setContent(documentHtml || '', false)
      // Small delay to avoid update loop
      setTimeout(() => {
        isExternalUpdate.current = false
      }, 50)
    }
  }, [documentHtml, editor])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current)
    }
  }, [])

  if (!editor) return null

  return (
    <div style={{ position: 'relative' }}>
      <EditorContent editor={editor} />
    </div>
  )
}
