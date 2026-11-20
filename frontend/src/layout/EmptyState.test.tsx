import { render, screen } from '@testing-library/react'
import { Inbox } from 'lucide-react'
import { describe, expect, it } from 'vitest'
import { EmptyState } from './EmptyState'

describe('EmptyState', () => {
  it('shows its text', () => {
    render(<EmptyState icon={Inbox}>Nessun dato.</EmptyState>)

    expect(screen.getByText('Nessun dato.')).toBeInTheDocument()
  })
})
