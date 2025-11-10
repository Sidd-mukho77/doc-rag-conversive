interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fadeIn px-2`}>
      <div
        className={`max-w-[85%] rounded-2xl px-6 py-4 shadow-lg ${
          isUser
            ? 'bg-gradient-to-br from-purple-600 to-pink-600 text-white'
            : 'bg-neutral-800/80 backdrop-blur-xl text-white border border-neutral-700/50'
        }`}
      >
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>
        <div className="text-xs opacity-50 mt-3">
          <span>{message.timestamp.toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  )
}
