/**
 * Local provider — Ollama via OpenAI-compatible API
 *
 * Uses the OpenAI SDK pointed at localhost. Zero cost, full privacy,
 * works offline. Best for the Monitor role and simple coding tasks.
 *
 * Models: whatever the user has pulled in Ollama
 */

import type {
  Provider,
  ProviderCapabilities,
  ProviderName,
  Message,
  ChatOptions,
  ChatResponse,
} from "./interface.js";

export class LocalProvider implements Provider {
  readonly name: ProviderName = "local";
  readonly capabilities: ProviderCapabilities = {
    chat: true,
    webSearch: false,
    agenticCode: false,
    toolUse: true, // partial — works with Qwen, Llama 3.1+
    longContext: false, // typically 32K-128K, not 1M
    thinking: false,
    streaming: true,
    batch: false,
  };

  private endpoint: string;
  private _availableModels: string[] = [];

  constructor(endpoint = "http://localhost:11434/v1") {
    this.endpoint = endpoint;
  }

  get availableModels(): string[] {
    return this._availableModels;
  }

  async chat(
    messages: Message[],
    options?: ChatOptions,
  ): Promise<ChatResponse> {
    // TODO: Implement via openai SDK with base_url pointed at Ollama
    // const client = new OpenAI({ baseURL: this.endpoint, apiKey: "ollama" });
    throw new Error("Not yet implemented");
  }

  async healthCheck(): Promise<boolean> {
    // TODO: Check if Ollama is running and responsive
    // try { fetch(`${this.endpoint}/models`) } ...
    return false;
  }

  /** Discover which models the user has pulled in Ollama */
  async discoverModels(): Promise<string[]> {
    // TODO: GET http://localhost:11434/api/tags
    // Parse response and populate _availableModels
    return [];
  }
}
