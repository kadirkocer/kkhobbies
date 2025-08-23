'use client'

import { Hobby } from '@/lib/shared/types'
import { 
  Music, Camera, Video, Book, Shirt, Cpu, 
  FolderOpen, Plus, Settings 
} from 'lucide-react'

interface SidebarProps {
  hobbies: Hobby[]
  selectedHobbyId: number | null
  onHobbySelect: (id: number | null) => void
}

const iconMap: Record<string, any> = {
  music: Music,
  camera: Camera,
  video: Video,
  book: Book,
  shirt: Shirt,
  cpu: Cpu,
}

export function Sidebar({ hobbies, selectedHobbyId, onHobbySelect }: SidebarProps) {
  const getIcon = (iconName: string = 'folder') => {
    const IconComponent = iconMap[iconName] || FolderOpen
    return <IconComponent className="w-5 h-5" />
  }

  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold text-white">Hobby Showcase</h1>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        <button
          onClick={() => onHobbySelect(null)}
          className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
            selectedHobbyId === null
              ? 'bg-blue-600 text-white'
              : 'text-gray-300 hover:bg-gray-700'
          }`}
        >
          <FolderOpen className="w-5 h-5" />
          <span>All Entries</span>
        </button>

        <div className="pt-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
              Hobbies
            </h3>
            <button className="text-gray-400 hover:text-white">
              <Plus className="w-4 h-4" />
            </button>
          </div>
          
          <div className="space-y-1">
            {hobbies.map((hobby) => (
              <button
                key={hobby.id}
                onClick={() => onHobbySelect(hobby.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                  selectedHobbyId === hobby.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <div 
                  className="w-5 h-5 rounded flex items-center justify-center text-xs"
                  style={{ backgroundColor: hobby.color || '#6B7280' }}
                >
                  {getIcon(hobby.icon)}
                </div>
                <span className="truncate">{hobby.name}</span>
              </button>
            ))}
          </div>
        </div>
      </nav>

      <div className="p-4 border-t border-gray-700">
        <button className="w-full flex items-center space-x-3 px-3 py-2 text-gray-300 hover:bg-gray-700 rounded-lg transition-colors">
          <Settings className="w-5 h-5" />
          <span>Settings</span>
        </button>
      </div>
    </div>
  )
}