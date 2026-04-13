/**
 * Provider interface — the unified abstraction across all LLM providers.
 *
 * Every provider (Claude, OpenAI, Gemini, Local/Ollama) implements this
 * interface. The router selects a provider based on role configuration.
 *
 * Design decisions:
 * - chat() is the universal primitive — all providers support it
 * - research() adds web search capability (not all providers support it)
 * - code() adds agentic code execution (only Claude Agent SDK and Codex SDK)
 * - Providers declare their capabilities so the router can make informed choices
 */

export interface Message {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface ToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, unknown>;
}

export interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
}

export interface ChatResponse {
  content: string;
  toolCalls?: ToolCall[];
  usage?: {
    inputTokens: number;
    outputTokens: number;
    cachedTokens?: number;
    costUsd?: number;
  };
  model: string;
  provider: ProviderName;
}

export interface ChatOptions {
  model?: string;
  temperature?: number;
  maxTokens?: number;
  tools?: ToolDefinition[];
  systemPrompt?: string;
  thinking?: boolean;
}

export interface ResearchOptions extends ChatOptions {
  webSearch?: boolean;
  maxSources?: number;
}

export interface CodeOptions {
  workingDirectory: string;
  allowedTools?: string[];
  maxBudgetUsd?: number;
  maxTurns?: number;
}

export type ProviderName = "claude" | "openai" | "gemini" | "local";

export interface ProviderCapabilities {
  chat: boolean;
  webSearch: boolean;
  agenticCode: boolean;
  toolUse: boolean;
  longContext: boolean; // 200k+ tokens
  thinking: boolean; // extended reasoning
  streaming: boolean;
  batch: boolean;
}

export interface Provider {
  readonly name: ProviderName;
  readonly capabilities: ProviderCapabilities;
  readonly availableModels: string[];

  /** Basic chat completion — all providers support this */
  chat(messages: Message[], options?: ChatOptions): Promise<ChatResponse>;

  /** Chat with web search grounding — not all providers support this */
  research?(
    messages: Message[],
    options?: ResearchOptions,
  ): Promise<ChatResponse>;

  /** Agentic code execution — only Claude Agent SDK and Codex SDK */
  code?(prompt: string, options?: CodeOptions): Promise<ChatResponse>;

  /** Check if the provider is configured and reachable */
  healthCheck(): Promise<boolean>;
}
