'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { hobbiesAPI, entriesAPI } from '@/lib/shared/client'
import { Sidebar } from './layout/sidebar'
import { TopBar } from './layout/top-bar'
import { EntryList } from './entries/entry-list'

export function Dashboard() {
  const [selectedHobbyId, setSelectedHobbyId] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  const { data: hobbies = [] } = useQuery({
    queryKey: ['hobbies'],
    queryFn: () => hobbiesAPI.getHobbies(),
  })

  const { data: entriesData, isLoading } = useQuery({
    queryKey: ['entries', selectedHobbyId, searchQuery],
    queryFn: () => entriesAPI.getEntries({
      hobby_id: selectedHobbyId || undefined,
      q: searchQuery || undefined,
      limit: 20,
    }),
  })

  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar
        hobbies={hobbies}
        selectedHobbyId={selectedHobbyId}
        onHobbySelect={setSelectedHobbyId}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
        />
        
        <main className="flex-1 overflow-auto p-6">
          <EntryList
            entries={entriesData?.items || []}
            isLoading={isLoading}
            selectedHobby={hobbies.find(h => h.id === selectedHobbyId)}
          />
        </main>
      </div>
    </div>
  )
}