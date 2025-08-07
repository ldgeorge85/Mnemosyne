# Frontend Architecture Guide

## Overview

The Mnemosyne frontend provides a chat-first AI assistant interface with perfect memory. Built using modern React patterns and proven component libraries, it delivers a familiar GPT-style experience while maintaining complete data sovereignty.

## Design Philosophy

### Component-Based Architecture
Rather than reinventing the wheel or maintaining a fork of existing chat UIs, we use:
- **shadcn/ui**: Copy-paste component library for rapid development
- **Radix UI**: Accessible, unstyled primitives as foundation
- **Tailwind CSS**: Utility-first styling for consistency

### Why This Approach?
1. **Maintenance**: No need to track upstream changes in forked projects
2. **Flexibility**: Pick exactly what we need, modify as required
3. **Modern Standards**: Uses the same patterns as ChatGPT, Claude, etc.
4. **Attribution**: Clear licensing with MIT-compatible components
5. **Performance**: Only ship what we use

## Core Technologies

### Framework & Build Tools
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type safety throughout
- **Vite**: Fast build tooling and HMR
- **React Router**: Client-side routing

### UI Components (shadcn/ui)
Copy-paste components we'll use:
```bash
# Core Components
- Button, Input, Label, Textarea
- Card, Dialog, Sheet, Popover
- Tabs, Accordion, Collapsible
- ScrollArea, Separator

# Form Components
- Form (react-hook-form integration)
- Select, Switch, Checkbox, Radio

# Feedback Components
- Toast, Alert, Badge
- Loading, Skeleton, Progress

# Data Display
- Avatar, Table, DataTable
- Command (command palette)
```

### Base Primitives (Radix UI)
Underlying accessible components:
- Dialog, Popover, Tooltip primitives
- Accordion, Tabs, Collapsible primitives
- ScrollArea with custom scrollbars
- Focus management and keyboard navigation

### Styling
- **Tailwind CSS**: Utility classes
- **CSS Variables**: Theme customization
- **Dark Mode**: System preference + manual toggle
- **Responsive Design**: Mobile-first approach

### State Management
- **Zustand**: Lightweight state management
- **React Query**: Server state and caching
- **Local Storage**: Preferences persistence

## Application Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   └── ...
│   │   ├── chat/
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatHistory.tsx
│   │   │   └── ChatContainer.tsx
│   │   ├── memory/
│   │   │   ├── MemoryList.tsx
│   │   │   ├── MemoryItem.tsx
│   │   │   ├── MemorySearch.tsx
│   │   │   └── MemoryFilters.tsx
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── AuthGuard.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── Layout.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx    # Main chat interface
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   └── Settings.tsx
│   ├── stores/
│   │   ├── auth.ts          # Authentication state
│   │   ├── chat.ts          # Chat messages & state
│   │   ├── memory.ts        # Memory management
│   │   └── ui.ts            # UI preferences
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   ├── utils.ts         # Utilities
│   │   └── constants.ts     # Constants
│   ├── styles/
│   │   └── globals.css      # Global styles & Tailwind
│   ├── App.tsx
│   └── main.tsx
```

## Core Features

### 1. Chat Interface (GPT-Style)
```typescript
// Standard chat UI pattern:
- Message list with markdown rendering
- Streaming responses with loading states
- Code syntax highlighting
- File attachments and image display
- Message actions (copy, edit, regenerate)
```

### 2. Memory Sidebar
```typescript
// Persistent context display:
- Chronological memory list
- Search and filtering
- Memory importance indicators
- Related memories clustering
- Quick memory actions
```

### 3. Authentication Flow
```typescript
// Secure user management:
- JWT-based authentication
- Register with email/password
- Persistent sessions
- Secure token refresh
```

### 4. Kartouche Visualization
```typescript
// Unique visual identity:
- SVG-based symbolic representation
- Dynamic generation from cognitive signature
- Interactive hover states
- Export capabilities
```

## UI/UX Patterns

### Chat-First Experience
1. **Primary Focus**: Chat input always visible and accessible
2. **Context Awareness**: Show relevant memories alongside conversation
3. **Progressive Disclosure**: Advanced features revealed as needed
4. **Keyboard Shortcuts**: Power user productivity

### Responsive Design
```css
/* Breakpoints */
- Mobile: < 640px (single column)
- Tablet: 640px - 1024px (collapsible sidebar)
- Desktop: > 1024px (full layout)
```

### Accessibility
- WCAG 2.1 AA compliance via Radix UI
- Keyboard navigation throughout
- Screen reader announcements
- High contrast mode support
- Focus indicators

## API Integration

### OpenAI-Compatible Format
```typescript
interface ChatRequest {
  messages: Message[];
  model?: string;
  temperature?: number;
  stream?: boolean;
}

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: {
    memories?: string[];
    importance?: number;
  };
}
```

### Memory Operations
```typescript
// CRUD operations for memories
GET    /api/v1/memories
POST   /api/v1/memories
PUT    /api/v1/memories/:id
DELETE /api/v1/memories/:id

// Search and filtering
POST   /api/v1/memories/search
GET    /api/v1/memories/related/:id
```

## Development Workflow

### Setup
```bash
cd frontend
npm install
npm run dev
```

### Adding shadcn/ui Components
```bash
# Manual copy from shadcn/ui repository
# 1. Copy component from shadcn/ui GitHub
# 2. Place in src/components/ui/
# 3. Update imports and styling
# 4. Add to ATTRIBUTION.md
```

### Building for Production
```bash
npm run build
npm run preview
```

## Performance Considerations

### Optimization Strategies
1. **Code Splitting**: Route-based lazy loading
2. **Memoization**: React.memo for expensive components
3. **Virtual Scrolling**: For long memory lists
4. **Debouncing**: Search and input handlers
5. **Image Optimization**: Lazy loading and compression

### Bundle Size Targets
- Initial JS: < 200KB
- Initial CSS: < 50KB
- Total cached: < 500KB

## Security Considerations

### Client-Side Security
1. **XSS Prevention**: Content sanitization
2. **CSRF Protection**: Token validation
3. **Secure Storage**: No sensitive data in localStorage
4. **HTTPS Only**: Enforce secure connections
5. **CSP Headers**: Strict content security policy

## Testing Strategy

### Unit Tests
```typescript
// Component testing with Vitest
- UI component behavior
- Store logic
- Utility functions
```

### Integration Tests
```typescript
// E2E with Playwright
- Authentication flow
- Chat interactions
- Memory operations
```

## Deployment

### Docker Container
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

### Environment Variables
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_NAME=Mnemosyne
```

## Future Enhancements

### Phase 1 (Current)
- Basic chat interface
- Memory sidebar
- Authentication

### Phase 2
- Real-time collaboration
- Voice input/output
- Mobile app (React Native)

### Phase 3
- Plugin system
- Custom themes
- Advanced visualizations

## Resources

- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [Radix UI Primitives](https://www.radix-ui.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Query](https://tanstack.com/query)
- [Zustand](https://zustand-demo.pmnd.rs/)

---

*Building a familiar yet sovereign interface for cognitive freedom.*