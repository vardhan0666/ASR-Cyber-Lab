/**
 * Global test environment setup, loaded via vite.config.ts's
 * test.setupFiles. Extends Vitest's `expect` with jest-dom's DOM-specific
 * matchers (toBeInTheDocument, toHaveAttribute, etc.) used throughout the
 * component test suite.
 */

import "@testing-library/jest-dom";