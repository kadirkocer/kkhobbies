'use client'

import { useRouter } from 'next/navigation'
import { LoginForm } from '@/components/auth/login-form'

export default function LoginPage() {
  const router = useRouter()

  const handleLoginSuccess = () => {
    router.push('/entries')
  }

  return <LoginForm onSuccess={handleLoginSuccess} />
}