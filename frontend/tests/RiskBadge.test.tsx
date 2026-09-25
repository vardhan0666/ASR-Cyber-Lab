/**
 * Unit tests for RiskBadge: label/score rendering, tooltip visibility
 * driven by the presence of an explanation array, and correct
 * focusability (tabIndex) based on whether a tooltip can be shown.
 */

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import RiskBadge from "../src/components/common/RiskBadge";

describe("RiskBadge", () => {
  it("renders the severity label and formatted risk score", () => {
    render(<RiskBadge severity="high" riskScore={75} />);

    expect(screen.getByText(/High/)).toBeInTheDocument();
    expect(screen.getByText(/75\.0\/100/)).toBeInTheDocument();
  });

  it("renders without a risk score when none is provided", () => {
    render(<RiskBadge severity="info" />);

    expect(screen.getByText(/Info/)).toBeInTheDocument();
    expect(screen.queryByText(/\/100/)).not.toBeInTheDocument();
  });

  it("shows the risk explanation tooltip on focus when explanation exists", () => {
    render(
      <RiskBadge
        severity="critical"
        riskScore={95}
        explanation={[
          "EVIDENCE: test evidence line",
          "RECOMMENDATION: test recommendation line",
        ]}
      />,
    );

    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();

    const trigger = screen.getByTestId("risk-badge-trigger");
    fireEvent.focus(trigger);

    expect(screen.getByRole("tooltip")).toBeInTheDocument();
    expect(screen.getByText(/test evidence line/)).toBeInTheDocument();
    expect(screen.getByText(/test recommendation line/)).toBeInTheDocument();

    fireEvent.blur(trigger);
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
  });

  it("is not keyboard-focusable and shows no tooltip when there is no explanation", () => {
    render(<RiskBadge severity="low" riskScore={20} />);

    const trigger = screen.getByTestId("risk-badge-trigger");
    expect(trigger).toHaveAttribute("tabindex", "-1");

    fireEvent.focus(trigger);
    expect(screen.queryByRole("tooltip")).not.toBeInTheDocument();
  });
});