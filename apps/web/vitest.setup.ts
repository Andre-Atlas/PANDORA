import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, beforeEach, vi } from "vitest";
import { simularMatchMedia } from "./test/matchMedia";

// Testes com `@vitest-environment node` não têm DOM.
const temDom = typeof window !== "undefined";

beforeEach(() => {
  if (temDom) simularMatchMedia(false);
});

afterEach(() => {
  // `ligarDadosReais()` (test/apiFalsa.ts) não pode vazar para o próximo teste.
  vi.unstubAllEnvs();
  if (!temDom) return;
  cleanup();
  localStorage.clear();
  sessionStorage.clear();
  document.title = "";
  delete document.documentElement.dataset.theme;
});
