import type * as PandoraDS from "@pandora/design-system";
import type * as ReactNS from "react";

/** Os componentes do design system, com os tipos de `components/index.d.ts`. */
export type Pandora = typeof PandoraDS;

declare global {
  interface Window {
    /** O bundle lê o React daqui, como faria com o React via <script>. */
    React?: typeof ReactNS;
    /** O bundle publica os componentes aqui. */
    Pandora?: Pandora;
  }
}
