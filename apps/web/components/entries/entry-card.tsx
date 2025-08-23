'use client'

import { EntryListItem } from '@/lib/shared/types'
import { Calendar, Tag, Image as ImageIcon } from 'lucide-react'

interface EntryCardProps {
  entry: EntryListItem
}

export function EntryCard({ entry }: EntryCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const getTags = (tags: string) => {
    return tags ? tags.split(',').map(t => t.trim()).filter(Boolean) : []
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors cursor-pointer">
      {entry.thumbnail_url && (
        <div className="aspect-video bg-gray-700 rounded-t-lg overflow-hidden">
          <img
            src={entry.thumbnail_url}
            alt={entry.title || 'Entry thumbnail'}
            className="w-full h-full object-cover"
          />
        </div>
      )}
      
      <div className="p-4">
        <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">
          {entry.title || 'Untitled Entry'}
        </h3>
        
        {entry.description && (
          <p className="text-gray-300 text-sm mb-3 line-clamp-2">
            {entry.description}
          </p>
        )}

        <div className="flex items-center justify-between text-xs text-gray-400 mb-3">
          <div className="flex items-center space-x-1">
            <Calendar className="w-3 h-3" />
            <span>{formatDate(entry.created_at)}</span>
          </div>
          
          {entry.media_count > 0 && (
            <div className="flex items-center space-x-1">
              <ImageIcon className="w-3 h-3" />
              <span>{entry.media_count}</span>
            </div>
          )}
        </div>

        {entry.tags && (
          <div className="flex flex-wrap gap-1 mb-3">
            {getTags(entry.tags).slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-700 text-gray-300"
              >
                <Tag className="w-3 h-3 mr-1" />
                {tag}
              </span>
            ))}
            {getTags(entry.tags).length > 3 && (
              <span className="text-xs text-gray-400">
                +{getTags(entry.tags).length - 3} more
              </span>
            )}
          </div>
        )}

        {Object.keys(entry.props).length > 0 && (
          <div className="border-t border-gray-700 pt-3 space-y-1">
            {Object.entries(entry.props).slice(0, 2).map(([key, value]) => (
              <div key={key} className="flex justify-between text-xs">
                <span className="text-gray-400 capitalize">{key}:</span>
                <span className="text-gray-300 truncate ml-2">{String(value)}</span>
              </div>
            ))}
            {Object.keys(entry.props).length > 2 && (
              <div className="text-xs text-gray-400">
                +{Object.keys(entry.props).length - 2} more properties
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}