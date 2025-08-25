'use client'

import { useState, useEffect } from 'react'
import { Plus, ChevronRight, ChevronDown } from 'lucide-react'
import { hobbiesAPI } from '@/lib/shared/client'
import { t } from '@/lib/i18n'
import { Hobby } from '@/lib/shared/types'

interface SidebarProps {
  onHobbySelect?: (hobbyId: number) => void
  selectedHobbyId?: number
}

export function Sidebar({ onHobbySelect, selectedHobbyId }: SidebarProps) {
  const [hobbies, setHobbies] = useState<Hobby[]>([])
  const [expandedHobbies, setExpandedHobbies] = useState<Set<number>>(new Set())
  const [showAddForm, setShowAddForm] = useState(false)
  const [newHobbyName, setNewHobbyName] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadHobbies()
  }, [])

  const loadHobbies = async () => {
    try {
      const tree = await hobbiesAPI.getHobbiesTree()
      const flat: Hobby[] = []
      const walk = (nodes: any[], parentId?: number) => {
        for (const n of nodes) {
          flat.push({
            id: n.id,
            name: n.name,
            color: n.color,
            icon: n.icon,
            parent_id: parentId,
            children: [],
          } as Hobby)
          if (n.children?.length) walk(n.children, n.id)
        }
      }
      walk(tree)
      setHobbies(flat)
    } catch (error) {
      console.error('Failed to load hobbies:', error)
    }
  }

  const handleAddHobby = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newHobbyName.trim()) return

    setIsLoading(true)
    try {
      await hobbiesAPI.createHobby({
        name: newHobbyName.trim(),
        color: '#6366f1',
        icon: 'folder',
        parent_id: selectedHobbyId
      })
      setNewHobbyName('')
      setShowAddForm(false)
      await loadHobbies()
    } catch (error) {
      console.error('Failed to create hobby:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleExpanded = (hobbyId: number) => {
    const newExpanded = new Set(expandedHobbies)
    if (newExpanded.has(hobbyId)) {
      newExpanded.delete(hobbyId)
    } else {
      newExpanded.add(hobbyId)
    }
    setExpandedHobbies(newExpanded)
  }

  const renderHobby = (hobby: Hobby, depth = 0) => {
    const hasChildren = hobbies.some(h => h.parent_id === hobby.id)
    const isExpanded = expandedHobbies.has(hobby.id)
    const isSelected = selectedHobbyId === hobby.id

    return (
      <div key={hobby.id}>
        <div
          className={`flex items-center gap-2 px-3 py-2 text-sm cursor-pointer hover:bg-gray-800 ${
            isSelected ? 'bg-blue-600 text-white' : 'text-gray-300'
          }`}
          style={{ paddingLeft: `${12 + depth * 16}px` }}
          onClick={() => onHobbySelect?.(hobby.id)}
        >
          {hasChildren && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                toggleExpanded(hobby.id)
              }}
              className="p-0.5 hover:bg-gray-700 rounded"
            >
              {isExpanded ? (
                <ChevronDown className="w-3 h-3" />
              ) : (
                <ChevronRight className="w-3 h-3" />
              )}
            </button>
          )}
          <div
            className="w-3 h-3 rounded-full flex-shrink-0"
            style={{ backgroundColor: hobby.color || '#6b7280' }}
          />
          <span className="truncate">{hobby.name}</span>
        </div>
        {hasChildren && isExpanded && (
          <div>
            {hobbies
              .filter(h => h.parent_id === hobby.id)
              .map(child => renderHobby(child, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  const topLevelHobbies = hobbies.filter(h => !h.parent_id)

  return (
    <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white mb-3">{t('nav.hobbies')}</h2>
        
        {showAddForm ? (
          <form onSubmit={handleAddHobby} className="space-y-2">
            <input
              type="text"
              value={newHobbyName}
              onChange={(e) => setNewHobbyName(e.target.value)}
              placeholder="Hobby name"
              className="w-full px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded text-white"
              autoFocus
            />
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={isLoading}
                className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                Add
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowAddForm(false)
                  setNewHobbyName('')
                }}
                className="px-2 py-1 text-xs bg-gray-700 text-white rounded hover:bg-gray-600"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <button
            onClick={() => setShowAddForm(true)}
            className="flex items-center gap-2 w-full px-2 py-1 text-sm text-gray-400 hover:text-white hover:bg-gray-800 rounded"
          >
            <Plus className="w-4 h-4" />
            {t('entry.new')}
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {topLevelHobbies.map(hobby => renderHobby(hobby))}
      </div>
    </div>
  )
}
