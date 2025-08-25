# Frontend Architecture Documentation

## Overview

The Mnemosyne frontend is a modern React application built with TypeScript, using Vite as the build tool. It implements a clean component-based architecture with Zustand for state management and shadcn/ui for the component library.

## Tech Stack

### Core Technologies
- **React 18** - UI framework with hooks and concurrent features
- **TypeScript** - Type safety and better developer experience
- **Vite** - Fast build tool with HMR
- **React Router v6** - Client-side routing

### UI & Styling
- **shadcn/ui** - Component library built on Radix UI
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **CSS Variables** - Design tokens for theming

### State & Data
- **Zustand** - Lightweight state management
- **React Context** - Authentication state
- **localStorage** - Persistent state storage

## Directory Structure

```
frontend/
├── src/
│   ├── api/                 # API Service Layer
│   │   ├── client-simple.ts # Fetch-based client (primary)
│   │   ├── client.ts        # Axios client (secondary)
│   │   ├── auth.ts          # Authentication services
│   │   ├── conversations.ts # Chat services
│   │   ├── memories.ts      # Memory services
│   │   └── tasks.ts         # Task services
│   ├── components/          # Reusable Components
│   │   ├── ui/             # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   └── ...
│   │   ├── TaskList.tsx    # Task list component
│   │   └── TaskForm.tsx    # Task creation form
│   ├── contexts/           # React Contexts
│   │   └── AuthContextSimple.tsx
│   ├── layouts/            # Layout Components
│   │   ├── AppShell.tsx   # Main app wrapper
│   │   └── SimpleSidebar.tsx # Navigation sidebar
│   ├── pages/              # Page Components
│   │   ├── Login.tsx       # Authentication
│   │   ├── DashboardMinimal.tsx
│   │   ├── ChatSimple.tsx  # Chat interface
│   │   ├── Tasks.tsx       # Task management
│   │   └── Memories.tsx    # Memory management
│   ├── router/             # Routing Configuration
│   │   └── index.tsx
│   ├── stores/             # Zustand Stores
│   │   ├── authStore.ts
│   │   ├── uiStore.ts
│   │   └── conversationStore.ts
│   ├── types/              # TypeScript Types
│   │   └── index.ts
│   ├── lib/                # Utilities
│   │   └── utils.ts
│   └── main.tsx           # Application Entry
├── public/                 # Static Assets
├── index.html             # HTML Entry
└── vite.config.ts         # Vite Configuration
```

## Architecture Patterns

### Component Architecture
```
Pages (Route-level components)
  └── Layouts (AppShell, Sidebar)
      └── Domain Components (TaskList, ChatBox)
          └── UI Components (Button, Card, Input)
```

### State Management Architecture
```
Global State (Zustand)
  ├── authStore (authentication state)
  ├── uiStore (UI preferences)
  └── conversationStore (chat data)

Context State
  └── AuthContext (auth wrapper with localStorage)

Local State
  └── useState/useReducer (component-specific)
```

### API Integration Pattern
```
Components
  └── Service Functions (api/*.ts)
      └── HTTP Client (client-simple.ts)
          └── Backend API
```

## Core Components

### Layout Components

#### AppShell (`/layouts/AppShell.tsx`)
Main application wrapper providing:
- Persistent navigation sidebar
- Responsive layout management
- Route outlet for page content

#### SimpleSidebar (`/layouts/SimpleSidebar.tsx`)
Navigation sidebar featuring:
- Collapsible design (desktop)
- Overlay mode (mobile)
- Chat history integration
- User profile section

### Page Components

#### Login (`/pages/Login.tsx`)
- Username/password authentication
- Development quick-login buttons
- Form validation
- Redirect on success

#### ChatSimple (`/pages/ChatSimple.tsx`)
- Message display area
- Input field with submit
- Streaming response support
- Viewport-relative scrolling

#### Tasks (`/pages/Tasks.tsx`)
- Task list display
- Task creation form
- Status management (pending/in-progress/completed)
- Gamification elements (toned down)

### UI Components (shadcn/ui)

All UI components follow the shadcn/ui pattern:
- Built on Radix UI primitives
- Styled with Tailwind CSS
- Customizable via className prop
- Consistent variant system

## State Management

### Zustand Stores

#### Auth Store
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (credentials) => Promise<void>;
  logout: () => void;
}
```

#### UI Store
```typescript
interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  loading: boolean;
  toggleTheme: () => void;
  toggleSidebar: () => void;
}
```

#### Conversation Store
```typescript
interface ConversationState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  fetchConversations: () => Promise<void>;
  sendMessage: (content) => Promise<void>;
}
```

### Context Providers

#### AuthContext
Wraps the application with authentication state:
- User information
- Login/logout functions
- Token management
- Protected route logic

## Routing

### Route Structure
```typescript
<Routes>
  {/* Public Routes */}
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />
  
  {/* Protected Routes with AppShell */}
  <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
    <Route path="/" element={<DashboardMinimal />} />
    <Route path="/dashboard" element={<DashboardMinimal />} />
    <Route path="/chat" element={<ChatSimple />} />
    <Route path="/tasks" element={<Tasks />} />
    <Route path="/memories" element={<Memories />} />
    <Route path="/settings" element={<Settings />} />
  </Route>
</Routes>
```

### Protected Routes
- Check authentication state
- Redirect to login if unauthenticated
- Preserve intended destination

## API Integration

### HTTP Client
Primary client uses fetch API with consistent patterns:

```typescript
const makeRequest = async <T>(
  method: string,
  url: string,
  data?: any
): Promise<ApiResponse<T>> => {
  const token = localStorage.getItem('token');
  
  const response = await fetch(url, {
    method,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  return handleResponse<T>(response);
};
```

### Service Layer
Each domain has dedicated service functions:

```typescript
// conversations.ts
export const conversationsService = {
  getConversations: () => get<PaginatedResponse<Conversation>>('/conversations'),
  getConversation: (id) => get<Conversation>(`/conversations/${id}`),
  createConversation: (title) => post<Conversation>('/conversations', { title }),
  deleteConversation: (id) => del(`/conversations/${id}`)
};
```

## Styling Architecture

### Design System
- CSS custom properties for design tokens
- Tailwind configuration for consistent spacing/colors
- Dark mode support via class-based theming

### Component Styling
```typescript
// Using cva for variant-based styling
const buttonVariants = cva(
  "base-styles",
  {
    variants: {
      variant: { default: "...", outline: "..." },
      size: { sm: "...", md: "...", lg: "..." }
    }
  }
);
```

## Build & Deployment

### Development
```bash
npm run dev        # Start Vite dev server
npm run build      # Production build
npm run preview    # Preview production build
npm run lint       # Run ESLint
npm run test       # Run tests
```

### Docker Configuration
```dockerfile
# Multi-stage build
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

### Production Considerations
- Static file serving via nginx
- API proxy configuration
- Proper cache headers
- SPA routing support
- Health check endpoint

## Performance Optimizations

### Code Splitting
- Route-based code splitting
- Lazy loading for heavy components
- Dynamic imports for optional features

### State Management
- Zustand for minimal re-renders
- React.memo for expensive components
- useMemo/useCallback where appropriate

### Asset Optimization
- Image optimization
- Font subsetting
- CSS purging (Tailwind)
- Compression (gzip/brotli)

## Security Considerations

### Current Implementation
- JWT token storage in localStorage
- Protected route components
- CORS handling
- XSS prevention via React

### Best Practices
- No sensitive data in localStorage
- Token expiration handling
- Secure API communication
- Input sanitization

## Testing Strategy

### Current Setup
- Vitest for unit testing
- React Testing Library
- MSW for API mocking

### Testing Approach
- Component testing
- Integration testing
- E2E testing (planned)

## Future Enhancements

### Planned Features
- WebSocket support for real-time updates
- PWA capabilities
- Offline support
- Advanced memory UI
- Collaborative features

### Technical Improvements
- Error boundary implementation
- Performance monitoring
- Analytics integration
- Accessibility improvements

---

This architecture provides a solid foundation for a modern, maintainable React application with room for growth and enhancement.