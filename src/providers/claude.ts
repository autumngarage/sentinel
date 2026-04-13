/**
 * Claude provider — Anthropic API + Claude Agent SDK
 *
 * Supports all roles. The Agent SDK mode wraps Claude Code as a subprocess,
 * giving full agentic coding capability (file editing, terminal, test running).
 *
 * Models: claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5
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

const CLAUDE_MODELS = [
  "claude-opus-4-6",
  "claude-sonnet-4-6",
  "claude-haiku-4-5",
] as const;

export class ClaudeProvider implements Provider {
  readonly name: ProviderName = "claude";
  readonly availableModels = [...CLAUDE_MODELS];
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
    // TODO: Implement via @anthropic-ai/sdk
    throw new Error("Not yet implemented");
  }

  async research(
    messages: Message[],
    options?: ResearchOptions,
  ): Promise<ChatResponse> {
    // TODO: Implement via Anthropic SDK with web_search tool
    throw new Error("Not yet implemented");
  }

  async code(
    prompt: string,
    options?: CodeOptions,
  ): Promise<ChatResponse> {
    // TODO: Implement via claude-agent-sdk (Claude Code as subprocess)
    throw new Error("Not yet implemented");
  }

  async healthCheck(): Promise<boolean> {
    // TODO: Verify ANTHROPIC_API_KEY is set and reachable
    return !!process.env.ANTHROPIC_API_KEY;
  }
}
