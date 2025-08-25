'use client'

import { Suspense, useState, useEffect } from 'react'
import { Search, Plus, Filter } from 'lucide-react'
import { t } from '@/lib/i18n'
import { entriesAPI, hobbyTypesAPI, searchAPI, usersAPI } from '@/lib/shared/client'
import { EntryListItem, HobbyType } from '@/lib/shared/types'
import { Sidebar } from '@/components/Sidebar'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'

function EntriesInner() {
  const [entries, setEntries] = useState<EntryListItem[]>([])
  const [hobbyTypes, setHobbyTypes] = useState<HobbyType[]>([])
  const params = useSearchParams()
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState(params.get('q') || '')
  const [selectedHobbyId, setSelectedHobbyId] = useState<number | undefined>(params.get('hobby_id') ? Number(params.get('hobby_id')) : undefined)
  const [selectedTypeKey, setSelectedTypeKey] = useState<string>(params.get('type_key') || '')
  const [selectedTag, setSelectedTag] = useState(params.get('tag') || '')
  const includeDesc = params.get('include_descendants') === 'true'
  const [isLoading, setIsLoading] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    // Check authentication first
    const checkAuth = async () => {
      try {
        await usersAPI.getCurrentUser()
        setIsAuthenticated(true)
      } catch (error) {
        setIsAuthenticated(false)
        router.push('/')
      }
    }

    checkAuth()
  }, [router])

  useEffect(() => {
    if (isAuthenticated) {
      loadHobbyTypes()
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (isAuthenticated) {
      loadEntries()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params, isAuthenticated])

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
      const qp: any = {}
      const qv = params.get('q'); if (qv) qp.q = qv
      const hv = params.get('hobby_id'); if (hv) qp.hobby_id = Number(hv)
      const tv = params.get('type_key'); if (tv) qp.type_key = tv
      const tag = params.get('tag'); if (tag) qp.tag = tag
      const inc = params.get('include_descendants'); if (inc === 'true') qp.include_descendants = true
      const data = qv ? await searchAPI.search({ ...qp, limit: 20, offset: 0 }) : await entriesAPI.getEntries(qp)
      setEntries(data.items)
    } catch (error) {
      console.error('Failed to load entries:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const sp = new URLSearchParams(params.toString())
    if (searchQuery) sp.set('q', searchQuery); else sp.delete('q')
    router.push(`/entries?${sp.toString()}`)
  }

  const updateParam = (key: string, value?: string) => {
    const sp = new URLSearchParams(params.toString())
    if (value && value.length) sp.set(key, value); else sp.delete(key)
    router.push(`/entries?${sp.toString()}`)
  }

  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  if (isAuthenticated === false) {
    return null // Will be redirected to home page
  }

  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar
        onHobbySelect={(id) => {
          if (id) router.push(`/hobbies/${id}?tab=entries`)
          else router.push('/entries')
        }}
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
              onChange={(e) => updateParam('type_key', e.target.value)}
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
              defaultValue={selectedTag}
              onBlur={(e) => updateParam('tag', e.target.value)}
              placeholder={t('filter.tag')}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white placeholder-gray-400"
            />
            <label className="flex items-center gap-2 text-gray-300 text-sm">
              <input type="checkbox" defaultChecked={includeDesc} onChange={(e)=>updateParam('include_descendants', e.target.checked ? 'true' : undefined)} />
              {t('filter.include_descendants')}
            </label>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {/* Active chips */}
          <div className="mb-3 flex flex-wrap gap-2">
            {params.get('q') && (
              <button onClick={()=>updateParam('q')} className="px-2 py-1 bg-gray-800 text-gray-200 rounded text-xs">q: {params.get('q')} ✕</button>
            )}
            {params.get('type_key') && (
              <button onClick={()=>updateParam('type_key')} className="px-2 py-1 bg-gray-800 text-gray-200 rounded text-xs">{t('filter.type')}: {params.get('type_key')} ✕</button>
            )}
            {params.get('tag') && (
              <button onClick={()=>updateParam('tag')} className="px-2 py-1 bg-gray-800 text-gray-200 rounded text-xs">{t('filter.tag')}: {params.get('tag')} ✕</button>
            )}
            {params.get('include_descendants') === 'true' && (
              <button onClick={()=>updateParam('include_descendants')} className="px-2 py-1 bg-gray-800 text-gray-200 rounded text-xs">{t('filter.include_descendants')} ✕</button>
            )}
          </div>
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

export default function EntriesPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-900 text-white p-6">...</div>}>
      <EntriesInner />
    </Suspense>
  )
}
