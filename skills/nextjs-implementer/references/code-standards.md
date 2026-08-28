# NextJS Architecture Standards

These are the team's official coding standards. Every file you produce must
comply with all of them. Where you find the existing codebase deviating from
these standards, flag it — do not silently adopt the wrong pattern.

---

## 1. Component Structure

Every component must follow a strict three-layer internal order:

```
1. Variable and state declarations  (useState, useRef, derived values, context reads)
2. JavaScript / logic functions     (event handlers, computed logic — no JSX here)
3. Return / rendering template      (JSX only — no business logic inline)
```

**✅ Correct:**
```tsx
'use client'
import { useState } from 'react'

const CounterComponent = () => {
  // 1. State declarations
  const [counter, setCounter] = useState(0)

  // 2. Logic functions
  const handlePlusClick = () => setCounter(prev => prev + 1)
  const handleMinusClick = () => setCounter(prev => prev - 1)

  // 3. Rendering
  return (
    <div>
      <button onClick={handlePlusClick}>plus</button>
      <div>{counter}</div>
      <button onClick={handleMinusClick}>minus</button>
    </div>
  )
}
```

**❌ Wrong — inline logic in JSX, uncontrolled state:**
```tsx
// ❌ let instead of useState — not reactive
let counter = 0

// ❌ Logic buried inside onClick handlers in JSX
<button onClick={() => { if (counter <= 0) { counter++ } }}>plus</button>
```

The reasoning: separating layers makes components easier to unit test (you can
test logic functions in isolation), easier to debug (you know exactly where to
look for each concern), and easier for code reviewers to follow.

---

## 2. Prop Drilling — Use Context for Anything Beyond One Level

Passing props through more than two component layers is not allowed. Use React
Context instead.

**❌ Wrong — prop drilling through B to reach C:**
```tsx
const A = () => <B displayText="hello" />
const B = ({ displayText }: { displayText: string }) => <C displayText={displayText} />
const C = ({ displayText }: { displayText: string }) => <div>{displayText}</div>
```

Every intermediate component re-renders when the parent updates, even if it
doesn't use the prop. Context avoids this.

**✅ Correct — Context pattern:**

Step 1: Create a typed context in `context/` (e.g. `context/StoreContext.tsx`):
```tsx
'use client'
import { createContext, useContext, useState, FC, ReactNode } from 'react'

interface StoreContextType {
  displayText: string
}

const StoreContext = createContext<StoreContextType | undefined>(undefined)

interface StoreProviderProps {
  children: ReactNode
}

export const StoreProvider: FC<StoreProviderProps> = ({ children }) => {
  const [displayText, setDisplayText] = useState('hello world')
  return (
    <StoreContext.Provider value={{ displayText }}>
      {children}
    </StoreContext.Provider>
  )
}

export const useStoreContext = () => {
  const context = useContext(StoreContext)
  if (!context) {
    throw new Error('useStoreContext must be used within a StoreProvider')
  }
  return context
}
```

Step 2: Wrap at the highest shared ancestor:
```tsx
const ParentComponent = () => (
  <StoreProvider>
    <A />
  </StoreProvider>
)
```

Step 3: Any child reads from the hook directly — no props passed down:
```tsx
const C = () => {
  const { displayText } = useStoreContext()
  return <div>{displayText}</div>
}
```

---

## 3. Component Design Principles

- **Composable:** Build with layout components (`<Layout>`, `<Sidebar>`,
  `<Header>`, `<ProductDetail>`). Prefer composition over configuration.
- **Typed:** TypeScript everywhere. No `any`. Props and context values must
  have explicit interfaces.
- **Progressive Enhancement:** Core functionality must work without JS where
  possible (use Server Components for static content).

---

## 4. Server Components vs Client Components

Default to **Server Components** in `app/`. Only reach for `'use client'` when
the component genuinely needs interactivity.

| Use Server Components for | Use Client Components for |
|---|---|
| Static product details, descriptions | Cart buttons, image selectors, modals |
| Category pages, SEO-critical content | Filters, stateful UI, animations |
| `fetch()` with caching/revalidation | Event handlers (`onClick`, `onChange`) |
| Smaller bundles, faster loads | `useState`, `useEffect`, `useRef` |

Keep `'use client'` boundaries as low in the tree as possible. A page that is
mostly static but has one interactive widget should be a Server Component with
a single `'use client'` leaf — not a fully client-rendered page.

---

## 5. Streaming and Suspense

Use `loading.tsx` alongside `page.tsx` for route-level loading states. For
component-level streaming (e.g. a section that loads slower than the rest of
the page), wrap it in `<Suspense>`:

```tsx
import { Suspense } from 'react'
import ProductDetails from '@/components/ProductDetails'
import RelatedProducts from '@/components/RelatedProducts'

export default function ProductPage({ params }: { params: { slug: string } }) {
  return (
    <div>
      <ProductDetails slug={params.slug} />
      <Suspense fallback={<div>Loading related products...</div>}>
        <RelatedProducts slug={params.slug} />
      </Suspense>
    </div>
  )
}
```

`RelatedProducts` streams in while `ProductDetails` renders immediately. The
fallback is shown only for the deferred section, not the whole page.

---

## 6. Error Handling

Every route segment must have a co-located `error.tsx`. It must be a Client
Component (Next.js requirement) and must give the user a recovery path:

```tsx
'use client'
import { useEffect } from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error
  reset: () => void
}) {
  useEffect(() => {
    console.error('Error rendering page:', error)
  }, [error])

  return (
    <div className="p-6 text-center">
      <h2 className="text-2xl font-bold text-red-600">Something went wrong!</h2>
      <p className="mt-2 text-gray-700">{error.message}</p>
      <button
        onClick={() => reset()}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Try again
      </button>
    </div>
  )
}
```

---

## 7. Unit Testing Standards

**Stack:** Jest + React Testing Library + MSW (Mock Service Worker)

**MSW for API mocking** — intercept at the network level, not with `jest.mock`
on fetch:

```ts
// __tests__/mocks/handlers.ts
import { rest } from 'msw'

export const handlers = [
  rest.get('/api/products', (req, res, ctx) =>
    res(ctx.status(200), ctx.json([{ id: 1, name: 'T-Shirt' }]))
  ),
]

// __tests__/mocks/server.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'
export const server = setupServer(...handlers)

// jest.setup.ts (or in each test file)
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

**Mocking Next.js modules** — use `jest.mock()` for `next/navigation` and
other Next.js internals:

```tsx
// __tests__/BackButton.test.tsx
import { render, fireEvent } from '@testing-library/react'
import BackButton from '@/components/BackButton'

jest.mock('next/navigation', () => ({
  useRouter: () => ({ back: jest.fn() }),
}))

describe('BackButton', () => {
  it('calls router.back when clicked', () => {
    const { getByText } = render(<BackButton />)
    fireEvent.click(getByText('Go Back'))
    expect(getByText('Go Back')).toBeInTheDocument()
  })
})
```

**Use `@testing-library/user-event`** for user interactions that need realistic
browser event simulation (over `fireEvent` for complex interactions).

**Test what the story requires.** Every acceptance criterion maps to at least
one test. Do not write tests that only assert the component exists.
