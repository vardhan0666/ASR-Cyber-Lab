import { useEffect } from "react";

export default function CustomCursor() {
  useEffect(() => {
    const mediaQuery = window.matchMedia("(pointer: fine)");

    if (!mediaQuery.matches) {
      return;
    }

    const root = document.documentElement;

    root.classList.add("asr-cursor-enabled");

    let clickTimer: number | undefined;

    const handlePointerMove = (event: PointerEvent) => {
      root.style.setProperty("--asr-cursor-x", `${event.clientX}px`);
      root.style.setProperty("--asr-cursor-y", `${event.clientY}px`);

      const target = event.target as HTMLElement | null;

      const interactive = Boolean(
        target?.closest(
          "a, button, input, select, textarea, [role='button'], [data-cursor='interactive']",
        ),
      );

      root.classList.toggle("asr-cursor-hover", interactive);
    };

    const handlePointerDown = () => {
      root.classList.add("asr-cursor-click");

      if (clickTimer !== undefined) {
        window.clearTimeout(clickTimer);
      }

      clickTimer = window.setTimeout(() => {
        root.classList.remove("asr-cursor-click");
      }, 180);
    };

    const handlePointerLeave = () => {
      root.style.setProperty("--asr-cursor-x", "-100px");
      root.style.setProperty("--asr-cursor-y", "-100px");
    };

    document.addEventListener("pointermove", handlePointerMove);
    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("pointerleave", handlePointerLeave);

    return () => {
      if (clickTimer !== undefined) {
        window.clearTimeout(clickTimer);
      }

      document.removeEventListener("pointermove", handlePointerMove);
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("pointerleave", handlePointerLeave);

      root.classList.remove(
        "asr-cursor-enabled",
        "asr-cursor-hover",
        "asr-cursor-click",
      );
    };
  }, []);

  return (
    <>
      <div
        className="asr-cursor"
        aria-hidden="true"
      />

      <div
        className="asr-cursor-ring"
        aria-hidden="true"
      />
    </>
  );
}