'use client'

import { useState, useEffect } from 'react'
import { Search, Plus, Filter } from 'lucide-react'
import { t } from '@/lib/i18n'
import { entriesAPI, hobbyTypesAPI } from '@/lib/shared/client'
import { EntryListItem, HobbyType } from '@/lib/shared/types'
import { Sidebar } from '@/components/Sidebar'
import Link from 'next/link'

export default function EntriesPage() {
  const [entries, setEntries] = useState<EntryListItem[]>([])
  const [hobbyTypes, setHobbyTypes] = useState<HobbyType[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedHobbyId, setSelectedHobbyId] = useState<number>()
  const [selectedTypeKey, setSelectedTypeKey] = useState<string>('')
  const [selectedTag, setSelectedTag] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadHobbyTypes()
    loadEntries()
  }, [])

  useEffect(() => {
    loadEntries()
  }, [searchQuery, selectedHobbyId, selectedTypeKey, selectedTag])

  const loadHobbyTypes = async () => {
    try {
      const data = await hobbyTypesAPI.getHobbyTypes()
      setHobbyTypes(data)
    } catch (error) {
      console.error('Failed to load hobby types:', error)
    }
  }

  const loadEntries = async () => {
    setIsLoading(true)
    try {
      const params: any = {}
      if (searchQuery) params.q = searchQuery
      if (selectedHobbyId) params.hobby_id = selectedHobbyId
      if (selectedTypeKey) params.type_key = selectedTypeKey
      if (selectedTag) params.tag = selectedTag
      
      const data = await entriesAPI.getEntries(params)
      setEntries(data.items)
    } catch (error) {
      console.error('Failed to load entries:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    loadEntries()
  }

  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar
        onHobbySelect={setSelectedHobbyId}
        selectedHobbyId={selectedHobbyId}
      />
      
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-gray-800 border-b border-gray-700 p-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-bold text-white">{t('tabs.entries')}</h1>
            <Link
              href="/entries/new"
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              {t('entry.new')}
            </Link>
          </div>

          {/* Search and Filters */}
          <div className="flex gap-4">
            <form onSubmit={handleSearch} className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t('search.placeholder')}
                  className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded text-white placeholder-gray-400"
                />
              </div>
            </form>

            <select
              value={selectedTypeKey}
              onChange={(e) => setSelectedTypeKey(e.target.value)}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white"
            >
              <option value="">{t('filter.type')}</option>
              {hobbyTypes.map(type => (
                <option key={type.key} value={type.key}>
                  {type.title}
                </option>
              ))}
            </select>

            <input
              type="text"
              value={selectedTag}
              onChange={(e) => setSelectedTag(e.target.value)}
              placeholder={t('filter.tag')}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white placeholder-gray-400"
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {isLoading ? (
            <div className="text-center text-gray-400 py-8">Loading...</div>
          ) : entries.length === 0 ? (
            <div className="text-center text-gray-400 py-8">
              {t('entry.empty')}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {entries.map(entry => (
                <Link
                  key={entry.id}
                  href={`/entries/${entry.id}`}
                  className="block bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors"
                >
                  <div className="aspect-video bg-gray-700 rounded mb-3 overflow-hidden">
                    {entry.thumbnail_url ? (
                      <img
                        src={entry.thumbnail_url}
                        alt={entry.title || 'Entry thumbnail'}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-500">
                        No image
                      </div>
                    )}
                  </div>
                  
                  <h3 className="font-semibold text-white mb-1 truncate">
                    {entry.title || 'Untitled'}
                  </h3>
                  
                  <p className="text-sm text-gray-400 mb-2 line-clamp-2">
                    {entry.description || 'No description'}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{entry.type_key}</span>
                    <span>{entry.media_count} media</span>
                  </div>
                  
                  {entry.tags && (
                    <div className="mt-2 text-xs text-blue-400">
                      {entry.tags}
                    </div>
                  )}
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
