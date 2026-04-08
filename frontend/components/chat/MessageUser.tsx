'use client'

import { Message } from '@/types'

interface Props {
  message: Message
}

export default function MessageUser({ message }: Props) {
  return (
    <div className="flex justify-end">
      <div className="message-user">{message.content}</div>
    </div>
  )
}
