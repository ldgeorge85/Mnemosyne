# Attribution & Licenses

This project incorporates ideas, patterns, and potentially code from various open source projects. We maintain this file to properly attribute these contributions.

## Component Libraries & Frameworks

### Core UI Components
- **@radix-ui** - MIT License
  - Unstyled, accessible UI components
  - Copyright (c) 2022 WorkOS
  - https://github.com/radix-ui/primitives

- **shadcn/ui** - MIT License
  - Component patterns and styling
  - Copyright (c) 2023 shadcn
  - https://github.com/shadcn-ui/ui
  - Note: Copy-paste library, not a dependency

- **Tailwind CSS** - MIT License
  - Utility-first CSS framework
  - Copyright (c) Tailwind Labs, Inc.
  - https://github.com/tailwindlabs/tailwindcss

### Chat UI Patterns & Inspiration

- **Chatbot UI** - MIT License
  - UI patterns and component structure inspiration
  - Copyright (c) 2024 Mckay Wrigley
  - https://github.com/mckaywrigley/chatbot-ui
  - Note: If we copy any code directly, we'll mark it clearly

### Security & Cryptography

- **OpenMLS** - MIT License
  - Rust implementation of MLS Protocol (RFC 9420)
  - Copyright OpenMLS Authors
  - https://github.com/openmls/openmls
  - Note: Using via Rust FFI bindings

- **libsodium** - ISC License
  - Cryptographic library
  - https://github.com/jedisct1/libsodium.js

### AI/LLM Frameworks

- **LangChain** - MIT License
  - LLM application framework
  - Copyright (c) Harrison Chase
  - https://github.com/langchain-ai/langchain

- **OpenAI Python** - MIT License
  - OpenAI API client
  - Copyright (c) OpenAI
  - https://github.com/openai/openai-python

## Code Attribution Policy

When copying code from other projects:

1. **Check License Compatibility**
   - MIT, BSD, Apache 2.0: Generally compatible
   - GPL: Need to consider implications
   - Custom licenses: Review carefully

2. **Mark Copied Code**
   ```typescript
   // Adapted from: https://github.com/mckaywrigley/chatbot-ui
   // Original License: MIT
   // Modifications: [describe what changed]
   ```

3. **Substantial Copying**
   - If copying entire files, preserve original copyright headers
   - Add our modifications notice below

4. **UI Patterns**
   - Common patterns (sidebar + chat) don't require attribution
   - Specific implementations should be credited

## License Compatibility Notes

- Projects with "no derivatives" or "share-alike" requirements need careful review
- GPL-licensed code requires understanding of viral licensing implications
- Always check for branding or attribution requirements beyond standard licensing

## Our License

The Mnemosyne Protocol itself is licensed under [TBD - need to decide].

Recommended options:
- MIT (maximum compatibility)
- Apache 2.0 (patent protection)
- AGPLv3 (if we want to ensure contributions back)

## Updates to This File

When adding new dependencies or copying code:
1. Add entry to appropriate section
2. Include license type and copyright
3. Note what we're using (inspiration vs direct code)
4. Commit with message: "Attribution: Add [project name]"

---

*Last updated: 2025-01-21*
*Maintained by: Project contributors*