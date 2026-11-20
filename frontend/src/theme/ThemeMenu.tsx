import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { Check, Monitor, Moon, Sun, type LucideIcon } from 'lucide-react'
import { useTheme, type ThemeChoice } from './useTheme'

const CHOICES: readonly { value: ThemeChoice; label: string; icon: LucideIcon }[] = [
  { value: 'light', label: 'Chiaro', icon: Sun },
  { value: 'dark', label: 'Scuro', icon: Moon },
  { value: 'system', label: 'Sistema', icon: Monitor },
]

export function ThemeMenu() {
  const { choice, setChoice } = useTheme()
  const ActiveIcon = CHOICES.find(({ value }) => value === choice)!.icon

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger
        aria-label="Tema"
        className="inline-flex size-10 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-surface-raised hover:text-foreground data-[state=open]:bg-surface-raised"
      >
        <ActiveIcon aria-hidden="true" className="size-5" />
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="end"
          sideOffset={8}
          className="z-50 min-w-40 rounded-lg border border-border bg-surface p-1 shadow-soft"
        >
          <DropdownMenu.RadioGroup value={choice} onValueChange={(value) => setChoice(value as ThemeChoice)}>
            {CHOICES.map(({ value, label, icon: Icon }) => (
              <DropdownMenu.RadioItem
                key={value}
                value={value}
                className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-2 text-sm outline-none data-[highlighted]:bg-surface-raised"
              >
                <Icon aria-hidden="true" className="size-4 text-muted-foreground" />
                {label}
                <DropdownMenu.ItemIndicator className="ml-auto">
                  <Check aria-hidden="true" className="size-4" />
                </DropdownMenu.ItemIndicator>
              </DropdownMenu.RadioItem>
            ))}
          </DropdownMenu.RadioGroup>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
