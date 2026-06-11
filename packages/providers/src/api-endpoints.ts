import type { ApiEndpointConfig } from "./provider-types";

export const officialOpenAIImageEndpoint: ApiEndpointConfig = {
  kind: "official",
  baseUrl: "https://api.openai.com/v1",
  apiKeyEnv: "OPENAI_API_KEY",
  defaultModel: "gpt-image-1"
};

export const aiaiGatewayEndpoint: ApiEndpointConfig = {
  kind: "gateway",
  baseUrl: "https://aiai.ac/api/v1",
  apiKeyEnv: "AIAI_API_KEY",
  defaultModel: "doubao-seedance-2.0"
};

export function resolveApiKey(config: ApiEndpointConfig): string {
  const value = process.env[config.apiKeyEnv];
  if (!value) {
    throw new Error(`Missing API key environment variable: ${config.apiKeyEnv}`);
  }
  return value;
}

export function joinEndpoint(baseUrl: string, path: string): string {
  const normalizedBase = baseUrl.replace(/\/+$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}
