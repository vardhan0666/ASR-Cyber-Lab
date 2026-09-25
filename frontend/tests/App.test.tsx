/**
 * Smoke test: an unauthenticated visitor loading the app should be
 * redirected to the login page rather than seeing protected content. No
 * network mocking is required here, since AuthContext only calls the
 * backend when a token is already present in localStorage, which is empty
 * by default in the test environment.
 */

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import App from "../src/App";

describe("App", () => {
  it("redirects unauthenticated users to the login page", async () => {
    render(<App />);

    expect(
      await screen.findByRole("heading", { name: /ASR-Cyber-Lab/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
    expect(
      screen.getByText(/authorized defensive security testing only/i),
    ).toBeInTheDocument();
  });
});