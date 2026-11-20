import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { PlaceholderPage } from './PlaceholderPage'

describe('PlaceholderPage', () => {
  it('shows title, description and empty state', () => {
    render(<PlaceholderPage title="Rosa" description="Qui ci sarà la rosa." emptyState="Nessun dato." />)

    expect(screen.getByRole('heading', { name: 'Rosa' })).toBeInTheDocument()
    expect(screen.getByText('Qui ci sarà la rosa.')).toBeInTheDocument()
    expect(screen.getByText('Nessun dato.')).toBeInTheDocument()
  })
})
