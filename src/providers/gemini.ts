/**
 * Gemini provider — Google GenAI SDK
 *
 * Particularly strong for research (native Google Search grounding)
 * and cost-effective scanning (Flash models at $0.30/MTok).
 *
 * Models: gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite
 */

import type {
  Provider,
  ProviderCapabilities,
  ProviderName,
  Message,
  ChatOptions,
  ChatResponse,
  ResearchOptions,
} from "./interface.js";

const GEMINI_MODELS = [
  "gemini-2.5-pro",
  "gemini-2.5-flash",
  "gemini-2.5-flash-lite",
] as const;

export class GeminiProvider implements Provider {
  readonly name: ProviderName = "gemini";
  readonly availableModels = [...GEMINI_MODELS];
  readonly capabilities: ProviderCapabilities = {
    chat: true,
    webSearch: true,
    agenticCode: false,
    toolUse: true,
    longContext: true,
    thinking: true,
    streaming: true,
    batch: true,
  };

  async chat(
    messages: Message[],
    options?: ChatOptions,
  ): Promise<ChatResponse> {
    // TODO: Implement via @google/genai SDK
    throw new Error("Not yet implemented");
  }

  async research(
    messages: Message[],
    options?: ResearchOptions,
  ): Promise<ChatResponse> {
    // TODO: Implement with Google Search grounding (native to API)
    // This is Gemini's killer feature — web search is built into the
    // API call, not a separate tool. The model can search and cite inline.
    throw new Error("Not yet implemented");
  }

  async healthCheck(): Promise<boolean> {
    return !!process.env.GEMINI_API_KEY;
  }
}
