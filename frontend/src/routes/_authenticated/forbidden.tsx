import { createFileRoute } from '@tanstack/react-router'
import { NotAuthorizedPage } from '@/layout/NotAuthorizedPage'

// Where the app goes when the API answers 403 to any call, for example after the role of the user changed.
export const Route = createFileRoute('/_authenticated/forbidden')({ component: NotAuthorizedPage })
