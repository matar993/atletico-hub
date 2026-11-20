import { createFileRoute } from '@tanstack/react-router'
import { NotificationsPage } from '@/notifications/NotificationsPage'

export const Route = createFileRoute('/_authenticated/notifications')({ component: NotificationsPage })
