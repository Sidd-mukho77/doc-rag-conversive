interface Source {
  title: string
  url: string
  relevance: number
}

export default function SourceCard({ source }: { source: Source }) {
  return (
    <div className="bg-white/5 backdrop-blur-xl rounded-xl p-4 border border-white/10 hover:border-purple-400/50 transition-all hover:scale-[1.02] hover:shadow-lg hover:shadow-purple-500/20 animate-fadeIn">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="text-sm font-semibold text-white truncate">
              {source.title}
            </h4>
          </div>
          <p className="text-xs text-white/50 truncate">{source.url}</p>
        </div>
        <div className="flex-shrink-0">
          <div className="px-3 py-1.5 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-full text-xs font-medium text-purple-300 border border-purple-400/30">
            {(source.relevance * 100).toFixed(0)}%
          </div>
        </div>
      </div>
    </div>
  )
}
