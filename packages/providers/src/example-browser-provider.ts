import { BrowserProviderBase } from "./browser-provider-base";

export class ExampleBrowserProvider extends BrowserProviderBase {
  constructor() {
    super("example-browser", "Example Browser Provider", "https://example.com");
  }
}
