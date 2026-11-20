import { createFileRoute } from '@tanstack/react-router'
import { CallUpsPage } from '@/call-ups/CallUpsPage'

export const Route = createFileRoute('/call-ups')({ component: CallUpsPage })
