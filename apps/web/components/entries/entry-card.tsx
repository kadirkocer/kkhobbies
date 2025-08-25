'use client'

import { useMemo } from 'react'
import { t } from '@/lib/i18n'
import Image from 'next/image'
import { EntryListItem } from '@/lib/shared/types'
import { Calendar, Tag, Image as ImageIcon } from 'lucide-react'

interface EntryCardProps {
  entry: EntryListItem
}

export function EntryCard({ entry }: EntryCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const tags = useMemo(() => {
    return entry.tags ? entry.tags.split(',').map(t => t.trim()).filter(Boolean) : []
  }, [entry.tags])

  const properties = useMemo(() => {
    return Object.entries(entry.props)
  }, [entry.props])

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors cursor-pointer">
      {entry.thumbnail_url && (
        <div className="aspect-video bg-gray-700 rounded-t-lg overflow-hidden">
          <Image
            src={entry.thumbnail_url}
            alt={entry.title || t('entry.thumbnail_alt')}
            className="w-full h-full object-cover"
            width={400}
            height={225}
          />
        </div>
      )}
      
      <div className="p-4">
        <h3 className="text-lg font-semibold text-white mb-2 line-clamp-2">
          {entry.title || t('entry.untitled')}
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

        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded text-xs bg-gray-700 text-gray-300"
              >
                <Tag className="w-3 h-3 mr-1" />
                {tag}
              </span>
            ))}
            {tags.length > 3 && (
              <span className="text-xs text-gray-400">
                +{tags.length - 3} {t('common.more')}
              </span>
            )}
          </div>
        )}

        {properties.length > 0 && (
          <div className="border-t border-gray-700 pt-3 space-y-1">
            {properties.slice(0, 2).map(([key, value]) => (
              <div key={key} className="flex justify-between text-xs">
                <span className="text-gray-400 capitalize">{key}:</span>
                <span className="text-gray-300 truncate ml-2">{String(value)}</span>
              </div>
            ))}
            {properties.length > 2 && (
              <div className="text-xs text-gray-400">
                +{properties.length - 2} {t('common.more_properties')}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}