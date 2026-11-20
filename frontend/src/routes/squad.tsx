import { createFileRoute } from '@tanstack/react-router'
import { SquadPage } from '@/squad/SquadPage'

export const Route = createFileRoute('/squad')({ component: SquadPage })
