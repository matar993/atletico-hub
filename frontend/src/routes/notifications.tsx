import { createFileRoute } from '@tanstack/react-router'
import { NotificationsPage } from '@/notifications/NotificationsPage'

export const Route = createFileRoute('/notifications')({ component: NotificationsPage })
