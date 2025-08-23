'use client'

import { EntryListItem, Hobby } from '@/lib/shared/types'
import { EntryCard } from './entry-card'

interface EntryListProps {
  entries: EntryListItem[]
  isLoading: boolean
  selectedHobby?: Hobby
}

export function EntryList({ entries, isLoading, selectedHobby }: EntryListProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (entries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-400">
        <div className="text-6xl mb-4">📝</div>
        <h3 className="text-xl font-medium mb-2">No entries yet</h3>
        <p className="text-center">
          {selectedHobby
            ? `Create your first entry for ${selectedHobby.name}`
            : 'Create your first hobby entry to get started'
          }
        </p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">
          {selectedHobby ? selectedHobby.name : 'All Entries'}
        </h2>
        <span className="text-gray-400">
          {entries.length} {entries.length === 1 ? 'entry' : 'entries'}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {entries.map((entry) => (
          <EntryCard key={entry.id} entry={entry} />
        ))}
      </div>
    </div>
  )
}