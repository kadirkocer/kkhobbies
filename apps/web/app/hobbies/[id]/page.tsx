'use client'

import { Suspense, useEffect, useMemo, useState } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { entriesAPI, searchAPI, hobbiesAPI, usersAPI } from '@/lib/shared/client'
import { EntryListItem, Hobby } from '@/lib/shared/types'
import { t } from '@/lib/i18n'
import { Sidebar } from '@/components/Sidebar'
import { Plus, Search, Filter, ArrowLeft } from 'lucide-react'
import Link from 'next/link'

type Tab = 'kayitlar' | 'kitaplik' | 'notes' | 'pdfs' | 'videos' | 'social' | 'baglantilar' | 'code' | 'music'

// Default tab configuration for hobbies
const DEFAULT_TABS: Tab[] = ['kayitlar', 'kitaplik', 'baglantilar', 'notes', 'pdfs', 'videos', 'social', 'code', 'music']

// Type key mappings for each tab
const TAB_TYPE_MAPPINGS: Record<Tab, string | string[] | null> = {
  kayitlar: null, // All types
  kitaplik: 'book',
  notes: 'note',
  pdfs: 'pdf_doc',
  videos: ['youtube_video'],
  social: 'social_post',
  baglantilar: ['bookmark', 'brand_link'],
  code: ['code_snippet', 'github_repo', 'project_link'],
  music: ['audio_track', 'spotify_playlist', 'spotify_track']
}

function HobbyInner() {
  const { id } = useParams<{id: string}>()
  const hobbyId = Number(id)
  const router = useRouter()
  const params = useSearchParams()
  const tab = (params.get('tab') as Tab) || 'kayitlar'
  
  const [hobby, setHobby] = useState<Hobby | null>(null)
  const [items, setItems] = useState<EntryListItem[]>([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [includeDescendants, setIncludeDescendants] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)

  // Available tabs based on hobby config
  const availableTabs = useMemo(() => {
    if (!hobby?.config_json) return DEFAULT_TABS
    try {
      const config = JSON.parse(hobby.config_json)
      return config.modules || DEFAULT_TABS
    } catch {
      return DEFAULT_TABS
    }
  }, [hobby])

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
      loadHobby()
    }
  }, [hobbyId, isAuthenticated])

  useEffect(() => {
    if (hobby && isAuthenticated) {
      loadItems()
    }
  }, [tab, hobby, searchQuery, includeDescendants, isAuthenticated])

  async function loadHobby() {
    try {
      const data = await hobbiesAPI.getHobby(hobbyId)
      setHobby(data)
    } catch (error) {
      console.error('Failed to load hobby:', error)
    }
  }

  async function loadItems() {
    if (!hobby) return
    
    setLoading(true)
    try {
      const typeMapping = TAB_TYPE_MAPPINGS[tab]
      let typeKeys: string[] = []

      if (typeMapping === null) {
        // All types for 'kayitlar'
        typeKeys = []
      } else if (typeof typeMapping === 'string') {
        typeKeys = [typeMapping]
      } else if (Array.isArray(typeMapping)) {
        typeKeys = typeMapping
      }

      let allItems: EntryListItem[] = []

      if (typeKeys.length === 0) {
        // Load all entries
        const searchParams: any = {
          hobby_id: hobbyId,
          include_descendants: includeDescendants
        }
        if (searchQuery) {
          searchParams.q = searchQuery
          const res = await searchAPI.search(searchParams)
          allItems = res.items
        } else {
          const res = await entriesAPI.getEntries(searchParams)
          allItems = res.items
        }
      } else {
        // Load entries for specific types
        for (const typeKey of typeKeys) {
          const searchParams: any = {
            hobby_id: hobbyId,
            include_descendants: includeDescendants,
            type_key: typeKey
          }
          if (searchQuery) {
            searchParams.q = searchQuery
            const res = await searchAPI.search(searchParams)
            allItems = allItems.concat(res.items)
          } else {
            const res = await entriesAPI.getEntries(searchParams)
            allItems = allItems.concat(res.items)
          }
        }
      }

      setItems(allItems)
    } catch (error) {
      console.error('Failed to load items:', error)
    } finally {
      setLoading(false)
    }
  }

  const setTab = (t: Tab) => {
    const sp = new URLSearchParams(params.toString())
    sp.set('tab', t)
    router.push(`/hobbies/${hobbyId}?${sp.toString()}`)
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    loadItems()
  }

  const getTabLabel = (tabKey: Tab): string => {
    switch (tabKey) {
      case 'kayitlar': return t('tabs.entries')
      case 'kitaplik': return t('tabs.library')
      case 'notes': return t('tabs.notes')
      case 'pdfs': return t('tabs.pdfs')
      case 'videos': return t('tabs.videos')
      case 'social': return t('tabs.social')
      case 'baglantilar': return t('tabs.links')
      case 'code': return t('tabs.code')
      case 'music': return t('tabs.music')
      default: return tabKey
    }
  }

  const renderAddButton = () => {
    const typeMapping = TAB_TYPE_MAPPINGS[tab]
    let addUrl = '/entries/new'
    
    if (typeMapping && typeof typeMapping === 'string') {
      addUrl = `/entries/new?type=${typeMapping}&hobby=${hobbyId}`
    } else if (typeMapping && Array.isArray(typeMapping) && typeMapping.length === 1) {
      addUrl = `/entries/new?type=${typeMapping[0]}&hobby=${hobbyId}`
    }

    return (
      <Link
        href={addUrl}
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        <Plus className="w-4 h-4" />
        {t('entry.new')}
      </Link>
    )
  }

  if (isAuthenticated === null || (!hobby && hobbyId)) {
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
          if (id) router.push(`/hobbies/${id}?tab=kayitlar`)
          else router.push('/entries')
        }}
        selectedHobbyId={hobbyId}
      />
      
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-gray-800 border-b border-gray-700 p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-4">
              <Link
                href="/entries"
                className="flex items-center gap-2 text-gray-400 hover:text-white"
              >
                <ArrowLeft className="w-4 h-4" />
                {t('nav.all_entries')}
              </Link>
              <h1 className="text-xl font-bold text-white">
                {hobby?.name || 'Hobby'}
              </h1>
            </div>
            {renderAddButton()}
          </div>

          {/* Search and Filters */}
          <div className="flex items-center gap-4 mb-4">
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

            <label className="flex items-center gap-2 text-gray-300 text-sm">
              <input 
                type="checkbox" 
                checked={includeDescendants}
                onChange={(e) => setIncludeDescendants(e.target.checked)}
              />
              {t('filter.include_descendants')}
            </label>
          </div>

          {/* Tabs */}
          <div className="flex items-center gap-2 overflow-x-auto">
            {availableTabs.map((tabKey: Tab) => (
              <button
                key={tabKey}
                onClick={() => setTab(tabKey)}
                className={`px-4 py-2 rounded whitespace-nowrap ${
                  tab === tabKey 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {getTabLabel(tabKey)}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center text-gray-400 py-8">Loading...</div>
          ) : items.length === 0 ? (
            <div className="text-center text-gray-400 py-8">
              <p className="mb-4">{t('entry.empty')}</p>
              <p className="text-sm">
                {hobby?.name ? t('entry.create_first').replace('{name}', hobby.name) : t('entry.create_first_generic')}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {items.map(entry => (
                <Link
                  key={entry.id}
                  href={`/entries/${entry.id}`}
                  className="block bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors"
                >
                  {/* Thumbnail */}
                  <div className="aspect-video bg-gray-700 rounded mb-3 overflow-hidden">
                    {entry.thumbnail_url ? (
                      <img
                        src={entry.thumbnail_url}
                        alt={entry.title || t('entry.untitled')}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-500">
                        <span className="text-xs">{entry.type_key.toUpperCase()}</span>
                      </div>
                    )}
                  </div>
                  
                  {/* Content */}
                  <div className="space-y-2">
                    <h3 className="font-semibold text-white mb-1 truncate">
                      {entry.title || t('entry.untitled')}
                    </h3>
                    
                    {entry.description && (
                      <p className="text-sm text-gray-400 line-clamp-2">
                        {entry.description}
                      </p>
                    )}
                    
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span className="px-2 py-1 bg-gray-700 rounded">
                        {entry.type_key}
                      </span>
                      {entry.media_count > 0 && (
                        <span>{entry.media_count} media</span>
                      )}
                    </div>
                    
                    {entry.tags && (
                      <div className="text-xs text-blue-400">
                        {entry.tags}
                      </div>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function HobbyPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gray-900 text-white p-6">Loading...</div>}>
      <HobbyInner />
    </Suspense>
  )
}