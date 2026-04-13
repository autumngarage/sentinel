/**
 * OpenAI provider — Responses API + Codex SDK
 *
 * Supports all roles. The Codex SDK mode provides agentic code execution
 * similar to Claude Agent SDK.
 *
 * Models: gpt-5.4, gpt-5.4-mini, gpt-5.3-codex, o4-mini
 */

import type {
  Provider,
  ProviderCapabilities,
  ProviderName,
  Message,
  ChatOptions,
  ChatResponse,
  ResearchOptions,
  CodeOptions,
} from "./interface.js";

const OPENAI_MODELS = [
  "gpt-5.4",
  "gpt-5.4-mini",
  "gpt-5.4-nano",
  "gpt-5.3-codex",
  "o4-mini",
  "o3",
] as const;

export class OpenAIProvider implements Provider {
  readonly name: ProviderName = "openai";
  readonly availableModels = [...OPENAI_MODELS];
  readonly capabilities: ProviderCapabilities = {
    chat: true,
    webSearch: true,
    agenticCode: true,
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
    // TODO: Implement via openai SDK (Responses API)
    throw new Error("Not yet implemented");
  }

  async research(
    messages: Message[],
    options?: ResearchOptions,
  ): Promise<ChatResponse> {
    // TODO: Implement via Responses API with web_search built-in tool
    throw new Error("Not yet implemented");
  }

  async code(
    prompt: string,
    options?: CodeOptions,
  ): Promise<ChatResponse> {
    // TODO: Implement via @openai/codex-sdk
    throw new Error("Not yet implemented");
  }

  async healthCheck(): Promise<boolean> {
    return !!process.env.OPENAI_API_KEY;
  }
}
