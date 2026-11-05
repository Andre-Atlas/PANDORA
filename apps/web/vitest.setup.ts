import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, beforeEach } from "vitest";
import { simularMatchMedia } from "./test/matchMedia";

beforeEach(() => {
  simularMatchMedia(false);
});

afterEach(() => {
  cleanup();
  localStorage.clear();
  sessionStorage.clear();
  document.title = "";
  delete document.documentElement.dataset.theme;
});
