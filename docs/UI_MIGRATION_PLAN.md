# UI Migration Plan: Chakra UI → shadcn/ui
## Pragmatic Approach for Mnemosyne Protocol

---

## Executive Summary

**Current State**: Chakra UI (working, deployed)  
**Target State**: shadcn/ui + Tailwind CSS  
**Timeline**: 4-6 weeks (low priority)  
**Approach**: Component-by-component migration  

---

## Why Migrate?

### Benefits of shadcn/ui
1. **Ownership**: Copy-paste means we own the code
2. **Performance**: No runtime CSS-in-JS overhead
3. **Flexibility**: Modify components as needed
4. **Modern**: Same patterns as ChatGPT, Claude
5. **Smaller bundle**: Only ship what we use

### Current Chakra UI Limitations
1. **Bundle size**: Entire framework shipped
2. **Customization**: Limited by framework
3. **Dependencies**: Tied to Chakra's release cycle
4. **Performance**: Runtime CSS generation

---

## Migration Strategy

### Phase 0: Preparation (Week 2)
✅ **Already Done**:
- Document current state
- Identify all Chakra components in use
- Create migration plan

⏳ **To Do**:
- Set up Tailwind alongside Chakra
- Install Radix UI primitives
- Create utilities file

### Phase 1: Foundation (Week 3)
1. Install dependencies:
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
   npm install class-variance-authority clsx tailwind-merge
   ```

2. Configure Tailwind:
   - Create `tailwind.config.js`
   - Add Tailwind directives to CSS
   - Set up CSS variables for theming

3. Create base components:
   - Button
   - Input
   - Card
   - Dialog

### Phase 2: Page Migration (Week 4)
Migrate pages in order of importance:

1. **Login Page** (simplest)
   - Convert Chakra form to shadcn/ui
   - Test authentication flow
   
2. **Dashboard/Chat** (most used)
   - Migrate chat components
   - Convert message list
   - Update input areas

3. **Settings** (least critical)
   - Convert forms
   - Migrate toggles and selects

### Phase 3: Component Library (Week 5)
Build shadcn/ui component library:

```
components/ui/
├── accordion.tsx
├── alert-dialog.tsx
├── alert.tsx
├── avatar.tsx
├── badge.tsx
├── button.tsx
├── card.tsx
├── checkbox.tsx
├── dialog.tsx
├── dropdown-menu.tsx
├── form.tsx
├── input.tsx
├── label.tsx
├── popover.tsx
├── progress.tsx
├── radio-group.tsx
├── scroll-area.tsx
├── select.tsx
├── separator.tsx
├── sheet.tsx
├── skeleton.tsx
├── slider.tsx
├── switch.tsx
├── table.tsx
├── tabs.tsx
├── textarea.tsx
├── toast.tsx
├── toaster.tsx
└── tooltip.tsx
```

### Phase 4: Cleanup (Week 6)
1. Remove Chakra dependencies
2. Remove Emotion
3. Update all imports
4. Performance testing
5. Bundle size analysis

---

## Component Mapping

### Priority 1: Core Components
| Chakra Component | shadcn/ui Replacement | Complexity |
|-----------------|----------------------|------------|
| Box/Flex | div with Tailwind | Simple |
| Button | button.tsx | Simple |
| Input | input.tsx | Simple |
| Textarea | textarea.tsx | Simple |
| Modal | dialog.tsx | Medium |
| Toast | toast.tsx | Medium |

### Priority 2: Layout Components
| Chakra Component | shadcn/ui Replacement | Complexity |
|-----------------|----------------------|------------|
| Container | div with max-w | Simple |
| Stack/HStack/VStack | flexbox utilities | Simple |
| Grid/SimpleGrid | grid utilities | Simple |
| Drawer | sheet.tsx | Medium |
| Tabs | tabs.tsx | Medium |

### Priority 3: Form Components
| Chakra Component | shadcn/ui Replacement | Complexity |
|-----------------|----------------------|------------|
| FormControl | form.tsx | Medium |
| Switch | switch.tsx | Simple |
| Checkbox | checkbox.tsx | Simple |
| Radio | radio-group.tsx | Simple |
| Select | select.tsx | Medium |

---

## Migration Checklist

### Pre-Migration
- [ ] Set up parallel Tailwind config
- [ ] Create component mapping document
- [ ] Install Radix UI dependencies
- [ ] Set up shadcn/ui utilities

### During Migration
- [ ] Maintain dual support temporarily
- [ ] Test each migrated component
- [ ] Update documentation
- [ ] Keep feature parity

### Post-Migration
- [ ] Remove Chakra dependencies
- [ ] Optimize bundle size
- [ ] Update all documentation
- [ ] Performance benchmarks

---

## Risk Mitigation

### Risks
1. **Breaking changes** during migration
2. **Lost functionality** from Chakra features
3. **Increased development time**
4. **Style inconsistencies**

### Mitigation Strategies
1. **Feature flags** for gradual rollout
2. **Component library** built incrementally
3. **Automated testing** for each component
4. **Style guide** maintained throughout

---

## Success Metrics

### Performance
- [ ] Bundle size reduced by >40%
- [ ] First paint improved by >20%
- [ ] Runtime performance improved

### Developer Experience
- [ ] Component customization easier
- [ ] Build times faster
- [ ] Less dependency management

### User Experience
- [ ] No visual regressions
- [ ] Improved responsiveness
- [ ] Better accessibility

---

## Decision Points

### Week 2 Review
- Is Chakra UI blocking any features?
- Are users complaining about performance?
- Do we have bandwidth for migration?

**If NO to all**: Defer migration to Month 2

### Week 4 Review
- Is partial migration working?
- Are there unexpected complications?
- Should we continue or rollback?

**If complications**: Maintain hybrid approach

---

## Alternative: Hybrid Approach

### Keep Chakra for:
- Complex components (DatePicker, etc.)
- Rapid prototyping
- Admin interfaces

### Use shadcn/ui for:
- Core user-facing components
- Performance-critical paths
- Highly customized components

---

## Conclusion

### Recommendation: **Defer Until Month 2**

**Rationale**:
1. Chakra UI is working fine
2. No user-facing issues
3. Higher priority work exists
4. Migration is optimization, not feature

### When to Revisit:
- After core features complete
- If performance becomes issue
- When team has bandwidth
- If customization needs increase

---

*"Ship first, optimize later. Don't fix what isn't broken."*