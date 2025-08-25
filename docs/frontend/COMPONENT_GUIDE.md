# Frontend Component Guide

## Overview

This guide documents all components in the Mnemosyne frontend, their usage, props, and examples.

## Layout Components

### AppShell
**Location:** `/src/layouts/AppShell.tsx`

Main application wrapper that provides the persistent navigation structure.

```tsx
// Usage (in router)
<Route element={<AppShell />}>
  <Route path="/dashboard" element={<DashboardMinimal />} />
</Route>
```

**Features:**
- Responsive sidebar management
- Mobile overlay support
- Route outlet for page content

### SimpleSidebar
**Location:** `/src/layouts/SimpleSidebar.tsx`

Navigation sidebar with collapsible functionality.

```tsx
interface SimpleSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onClose: () => void;
}
```

**Features:**
- Collapsible/expandable
- Chat history integration
- Navigation items with icons
- User profile section

## Page Components

### Login
**Location:** `/src/pages/Login.tsx`

Authentication page with login form.

**Features:**
- Email/username and password fields
- Form validation
- Quick login buttons (dev mode)
- Redirect after successful login

### DashboardMinimal
**Location:** `/src/pages/DashboardMinimal.tsx`

Main dashboard showing system overview.

**Features:**
- Stats cards (memories, tasks, etc.)
- Navigation to main features
- User welcome message

### ChatSimple
**Location:** `/src/pages/ChatSimple.tsx`

Chat interface for AI conversations.

**Features:**
- Message history display
- Input field with submit
- Streaming response support
- Proper scrolling behavior

### Tasks
**Location:** `/src/pages/Tasks.tsx`

Task management interface.

**Features:**
- Task list display
- Create new task button
- Task filtering
- Status management

## Domain Components

### TaskList
**Location:** `/src/components/TaskList.tsx`

Displays a list of tasks with actions.

```tsx
interface TaskListProps {
  onCreateClick?: () => void;
}
```

**Features:**
- Task cards with details
- Status badges
- Start/complete actions
- Priority indicators
- Completed count display

### TaskForm
**Location:** `/src/components/TaskForm.tsx`

Form for creating new tasks.

```tsx
interface TaskFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}
```

**Fields:**
- Title (required)
- Description
- Priority selector
- Task type selector
- Difficulty slider

## UI Components (shadcn/ui)

### Button
**Location:** `/src/components/ui/button.tsx`

Versatile button component with variants.

```tsx
interface ButtonProps {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  asChild?: boolean;
}

// Usage
<Button variant="outline" size="sm" onClick={handleClick}>
  Click me
</Button>
```

### Card
**Location:** `/src/components/ui/card.tsx`

Container component for content sections.

```tsx
// Usage
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>
    Content here
  </CardContent>
  <CardFooter>
    Footer content
  </CardFooter>
</Card>
```

### Input
**Location:** `/src/components/ui/input.tsx`

Form input component with consistent styling.

```tsx
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

// Usage
<Input 
  type="email" 
  placeholder="Enter email" 
  value={email}
  onChange={(e) => setEmail(e.target.value)}
/>
```

### Label
**Location:** `/src/components/ui/label.tsx`

Form label component.

```tsx
// Usage
<Label htmlFor="email">Email Address</Label>
<Input id="email" type="email" />
```

### Badge
**Location:** `/src/components/ui/badge.tsx`

Small status indicator component.

```tsx
interface BadgeProps {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
}

// Usage
<Badge variant="secondary">In Progress</Badge>
```

## Context Components

### AuthContextSimple
**Location:** `/src/contexts/AuthContextSimple.tsx`

Provides authentication state and functions.

```tsx
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

// Usage
const { user, login, logout } = useAuth();
```

### ProtectedRouteSimple
**Location:** `/src/components/auth/ProtectedRouteSimple.tsx`

Wrapper for routes requiring authentication.

```tsx
// Usage
<Route element={
  <ProtectedRouteSimple>
    <DashboardMinimal />
  </ProtectedRouteSimple>
} />
```

## Store Hooks

### useAuthStore
**Location:** `/src/stores/authStore.ts`

Authentication state management.

```tsx
// Usage
const { user, token, setUser, clearAuth } = useAuthStore();
```

### useUIStore
**Location:** `/src/stores/uiStore.ts`

UI preferences and state.

```tsx
// Usage
const { theme, sidebarOpen, toggleTheme, toggleSidebar } = useUIStore();
```

### useConversationStore
**Location:** `/src/stores/conversationStore.ts`

Chat conversation management.

```tsx
// Usage
const { 
  conversations, 
  currentConversation,
  fetchConversations,
  sendMessage 
} = useConversationStore();
```

## Utility Functions

### cn (className utility)
**Location:** `/src/lib/utils.ts`

Combines class names with conflict resolution.

```tsx
import { cn } from '@/lib/utils';

// Usage
<div className={cn(
  "base-class",
  condition && "conditional-class",
  className // prop
)} />
```

## Component Patterns

### Loading States
```tsx
if (loading) {
  return <div className="p-4">Loading...</div>;
}
```

### Error Handling
```tsx
{error && (
  <div className="text-red-500 text-sm">{error}</div>
)}
```

### Empty States
```tsx
{items.length === 0 ? (
  <Card>
    <CardContent className="py-8 text-center">
      <p className="text-muted-foreground">No items yet</p>
    </CardContent>
  </Card>
) : (
  // Display items
)}
```

### Form Submission
```tsx
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setLoading(true);
  setError(null);
  
  try {
    await submitData(formData);
    onSuccess?.();
  } catch (err) {
    setError('Failed to submit');
  } finally {
    setLoading(false);
  }
};
```

## Styling Patterns

### Responsive Design
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Responsive grid */}
</div>
```

### Dark Mode Support
```tsx
<div className="bg-background text-foreground">
  {/* Automatically adapts to theme */}
</div>
```

### Conditional Styling
```tsx
<div className={cn(
  "transition-colors",
  isActive ? "bg-accent" : "hover:bg-accent"
)}>
```

## Best Practices

### Component Organization
1. Keep components focused on a single responsibility
2. Extract reusable logic into custom hooks
3. Use TypeScript interfaces for props
4. Provide default props where appropriate

### State Management
1. Use local state for component-specific data
2. Use Zustand stores for global state
3. Use Context for cross-cutting concerns
4. Avoid prop drilling

### Performance
1. Use React.memo for expensive components
2. Implement useMemo/useCallback where needed
3. Lazy load heavy components
4. Optimize re-renders

### Accessibility
1. Use semantic HTML elements
2. Provide proper ARIA labels
3. Ensure keyboard navigation works
4. Test with screen readers

---

*For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md)*