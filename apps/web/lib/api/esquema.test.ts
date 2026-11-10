// @vitest-environment node
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import openapiTS, { COMMENT_HEADER, astToString } from "openapi-typescript";
import { describe, expect, it } from "vitest";

const ler = (relativo: string) => readFileSync(fileURLToPath(new URL(relativo, import.meta.url)), "utf8");

describe("tipos da API", () => {
  it("esquema.d.ts está em dia com apps/api/openapi.json", async () => {
    const contrato = JSON.parse(ler("../../../api/openapi.json"));
    const gerado = COMMENT_HEADER + astToString(await openapiTS(contrato));
    expect(ler("./esquema.d.ts") === gerado, "Tipos desatualizados. Rode: npm run api:tipos -w @pandora/web").toBe(true);
  });
});
