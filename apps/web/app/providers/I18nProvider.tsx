'use client'

import { ReactNode, useEffect } from 'react'
import { setLocale } from '@/lib/i18n'

export default function I18nProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    setLocale('tr')
  }, [])
  return <>{children}</>
}

