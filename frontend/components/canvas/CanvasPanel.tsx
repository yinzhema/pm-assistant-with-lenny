'use client'

import CanvasToolbar from '@/components/canvas/CanvasToolbar'
import TiptapEditor from '@/components/canvas/TiptapEditor'

export default function CanvasPanel() {
  return (
    <div
      className="canvas-panel"
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden',
      }}
    >
      <CanvasToolbar />
      <div style={{ flex: 1, overflowY: 'auto', padding: '0 1.5rem 2rem' }}>
        <TiptapEditor />
      </div>
    </div>
  )
}
