---
description: "Standards for UI development. Focus on design quality, accessibility, performance, and user experience."
alwaysApply: false
globs:
  - "apps/ui/**"
  - "components/**"
---

# Cursor Rules for Person 5: UI (Evidence-First Interface)

## Core Principles

**You are building the trust layer. The UI is what people see and interact with. It must be beautiful, clear, and opinionated. No ambiguity, no questions.**

### Design Standards

1. **Opinionated design**
   - Every UI element must have clear purpose
   - Every UI element must have contextual explanation
   - No ambiguity - if user wonders "what does this mean?", design failed
   - Use tooltips, labels, and help text liberally

2. **Visual hierarchy**
   - Most important information is most prominent
   - Use size, color, and spacing to create hierarchy
   - Primary actions are obvious
   - Secondary actions are discoverable but not distracting

3. **Consistency**
   - Use design system tokens consistently
   - Same patterns for similar actions
   - Consistent spacing, typography, colors
   - Consistent error states, loading states, empty states

4. **Accessibility**
   - All interactive elements must be keyboard accessible
   - All images must have alt text
   - Color contrast must meet WCAG AA standards
   - Screen reader friendly (proper ARIA labels)

### Code Quality Standards

1. **Type safety**
   - Use TypeScript strictly (no `any` types)
   - Define interfaces for all data structures
   - Use type guards for runtime validation
   - Validate API responses with Zod or similar

2. **Component organization**
   - One component per file
   - Components should be small and focused (<200 lines)
   - Extract reusable logic into custom hooks
   - Use composition over inheritance

3. **Performance**
   - Lazy load heavy components (Knowledge Graph)
   - Memoize expensive calculations
   - Use React.memo for expensive components
   - Optimize re-renders (use useMemo, useCallback)
   - Code split routes (Next.js automatic)

4. **Error handling**
   - All API calls must have error handling
   - Show user-friendly error messages
   - Never show stack traces to users
   - Log errors to console (development) or error tracking (production)

5. **Loading states**
   - Show loading indicators for all async operations
   - Use skeleton screens for better UX
   - Never leave user wondering if something is happening
   - Handle slow network gracefully

### API Integration Standards

1. **Error handling**
   - Handle all HTTP error codes (400, 401, 403, 404, 500, 503)
   - Show user-friendly error messages
   - Retry on transient failures (network errors)
   - Never crash on API errors

2. **Request management**
   - Use correlation IDs for all requests
   - Cancel requests when component unmounts
   - Debounce search inputs
   - Throttle rapid API calls

3. **Data fetching**
   - Use React Query or SWR for data fetching
   - Cache API responses appropriately
   - Invalidate cache on mutations
   - Handle stale data gracefully

4. **Optimistic updates**
   - Update UI optimistically when appropriate
   - Rollback on error
   - Show loading state during update

### Component Standards

1. **Reusability**
   - Extract common patterns into reusable components
   - Use composition over configuration
   - Make components flexible but opinionated
   - Document component props and usage

2. **Props validation**
   - Use TypeScript for prop types
   - Validate required props
   - Provide default values when appropriate
   - Document all props

3. **State management**
   - Use local state for component-specific state
   - Use context for shared state (sparingly)
   - Use URL state for shareable state (filters, search)
   - Avoid prop drilling (use context or composition)

4. **Side effects**
   - Use useEffect for side effects
   - Clean up side effects (cancel subscriptions, timers)
   - Handle race conditions (cancel requests on unmount)
   - Use proper dependencies in useEffect

### Knowledge Graph Standards

1. **Performance**
   - Lazy load 3D graph (only load when page is visible)
   - Use Web Workers for heavy calculations (if needed)
   - Optimize rendering (limit nodes/edges displayed)
   - Use level-of-detail (show fewer nodes when zoomed out)

2. **Interactivity**
   - Smooth animations (60fps)
   - Responsive to user input (drag, zoom, click)
   - Clear visual feedback (hover states, selection)
   - Keyboard shortcuts for common actions

3. **Data management**
   - Load nodes/edges incrementally (pagination)
   - Filter data on server side (not client side)
   - Cache graph data appropriately
   - Handle large datasets gracefully

### Testing Standards

1. **Unit tests**
   - Test all utility functions
   - Test all custom hooks
   - Test component rendering
   - Test user interactions

2. **Integration tests**
   - Test complete user flows
   - Test API integration
   - Test error scenarios
   - Test loading states

3. **E2E tests**
   - Test critical paths (create work item, override, view stats)
   - Test knowledge graph interaction
   - Test responsive design
   - Test accessibility

### Performance Standards

1. **Page load**
   - First Contentful Paint <1.5 seconds
   - Time to Interactive <3 seconds
   - Lighthouse score >90

2. **Runtime performance**
   - Smooth scrolling (60fps)
   - Responsive interactions (<100ms)
   - No janky animations
   - Efficient re-renders

3. **Bundle size**
   - Code split routes
   - Lazy load heavy dependencies
   - Tree shake unused code
   - Optimize images

### Accessibility Standards

1. **Keyboard navigation**
   - All interactive elements must be keyboard accessible
   - Logical tab order
   - Focus indicators visible
   - Keyboard shortcuts for common actions

2. **Screen readers**
   - Proper ARIA labels
   - Semantic HTML
   - Live regions for dynamic content
   - Skip links for navigation

3. **Visual accessibility**
   - Color contrast meets WCAG AA
   - Don't rely on color alone (use icons, text)
   - Text is readable (proper font size, line height)
   - Focus indicators are visible

### Error Handling Standards

1. **User-friendly errors**
   - Never show stack traces
   - Explain what went wrong in plain language
   - Suggest what user can do
   - Provide links to help or support

2. **Error boundaries**
   - Use React error boundaries
   - Catch errors gracefully
   - Show fallback UI
   - Log errors to error tracking

3. **Network errors**
   - Handle offline state
   - Retry on network errors
   - Show connection status
   - Queue actions when offline

### Documentation Standards

1. **Component documentation**
   - Document all components with JSDoc
   - Include usage examples
   - Document all props
   - Document component behavior

2. **Code comments**
   - Explain "why", not "what"
   - Comment complex logic
   - Document non-obvious decisions
   - Keep comments up to date

### Security Standards

1. **Input validation**
   - Validate all user inputs
   - Sanitize data before displaying
   - Prevent XSS attacks
   - Use Content Security Policy

2. **API security**
   - Never expose API keys in client code
   - Use environment variables
   - Validate API responses
   - Handle authentication properly

### Design System Standards

1. **Consistency**
   - Use design tokens consistently
   - Follow spacing scale
   - Use typography scale
   - Use color palette consistently

2. **Responsive design**
   - Mobile-first approach
   - Breakpoints: mobile (320px), tablet (768px), desktop (1024px)
   - Test on multiple screen sizes
   - Handle touch interactions

3. **Dark mode**
   - Support dark mode (off-black background)
   - Use design tokens for colors
   - Test contrast in dark mode
   - Provide theme toggle (if needed)

### Testing Checklist

- [ ] Unit tests for all utility functions
- [ ] Unit tests for all custom hooks
- [ ] Integration tests for all pages
- [ ] E2E tests for critical paths
- [ ] Accessibility tests (keyboard navigation, screen readers)
- [ ] Performance tests (page load, runtime)
- [ ] Responsive design tests
- [ ] Error handling tests
- [ ] Loading state tests
- [ ] Empty state tests

### Code Review Checklist

Before submitting code, ensure:
- [ ] All tests pass
- [ ] No linter errors
- [ ] TypeScript strict mode passes
- [ ] Components are accessible
- [ ] Error handling is comprehensive
- [ ] Loading states are implemented
- [ ] Performance is acceptable
- [ ] Design is consistent
- [ ] Documentation is updated
- [ ] No hardcoded values
- [ ] Responsive design works
- [ ] Dark mode works (if applicable)

---

**Remember: You are building the trust layer. The UI is what people see and interact with. It must be beautiful, clear, and opinionated. No ambiguity, no questions. Every element must have purpose, every action must be clear, every state must be handled.**

