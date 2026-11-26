import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, beforeEach } from "vitest";
import { simularMatchMedia } from "./test/matchMedia";

// Testes com `@vitest-environment node` não têm DOM.
const temDom = typeof window !== "undefined";

beforeEach(() => {
  if (temDom) simularMatchMedia(false);
});

afterEach(() => {
  if (!temDom) return;
  cleanup();
  localStorage.clear();
  sessionStorage.clear();
  document.title = "";
  delete document.documentElement.dataset.theme;
});
