import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Page } from './Page'

describe('Page', () => {
  it('shows one level 1 heading, with the eyebrow above and the description below', () => {
    render(<Page eyebrow="Squadra" title="Rosa" description="I giocatori." />)

    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1)
    expect(screen.getByRole('heading', { name: 'Rosa' })).toBeInTheDocument()
    expect(screen.getByText('Squadra')).toBeInTheDocument()
    expect(screen.getByText('I giocatori.')).toBeInTheDocument()
  })

  it('shows the actions and the content when given', () => {
    render(
      <Page title="Rosa" description="I giocatori." actions={<button>Aggiungi</button>}>
        <p>Contenuto</p>
      </Page>,
    )

    expect(screen.getByRole('button', { name: 'Aggiungi' })).toBeInTheDocument()
    expect(screen.getByText('Contenuto')).toBeInTheDocument()
  })

  it('omits the eyebrow and the actions when not given', () => {
    render(<Page title="Rosa" description="I giocatori." />)

    expect(screen.queryByRole('button')).not.toBeInTheDocument()
    expect(screen.getAllByText(/./)).toHaveLength(2)
  })
})
