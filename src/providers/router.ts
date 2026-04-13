/**
 * Router — selects the right provider for each role.
 *
 * The router reads the project's sentinel config to determine which
 * provider is assigned to each role, instantiates the providers,
 * and exposes role-based methods.
 *
 * The key insight: the user configures roles, not models. The router
 * translates role assignments into provider calls.
 */

import type { Provider, ProviderName, ChatResponse, Message } from "./interface.js";
import type { RoleName, RoleConfig, SentinelConfig } from "../config/schema.js";

export class Router {
  private providers: Map<ProviderName, Provider> = new Map();
  private roleMap: Map<RoleName, Provider> = new Map();

  constructor(config: SentinelConfig) {
    // TODO: Instantiate providers based on config
    // TODO: Map roles to providers
  }

  /** Get the provider assigned to a role */
  getProvider(role: RoleName): Provider {
    const provider = this.roleMap.get(role);
    if (!provider) {
      throw new Error(`No provider configured for role: ${role}`);
    }
    return provider;
  }

  /** Chat using the provider assigned to a specific role */
  async chat(role: RoleName, messages: Message[]): Promise<ChatResponse> {
    const provider = this.getProvider(role);
    return provider.chat(messages);
  }

  /** Research using the researcher role's provider */
  async research(messages: Message[]): Promise<ChatResponse> {
    const provider = this.getProvider("researcher");
    if (!provider.research) {
      // Fallback to regular chat if provider doesn't support research
      return provider.chat(messages);
    }
    return provider.research(messages);
  }

  /** Execute code using the coder role's provider */
  async code(prompt: string, workingDirectory: string): Promise<ChatResponse> {
    const provider = this.getProvider("coder");
    if (!provider.code) {
      throw new Error(
        `Provider ${provider.name} does not support agentic code execution. ` +
        `Consider using claude or openai for the coder role.`,
      );
    }
    return provider.code(prompt, { workingDirectory });
  }

  /** Health check all configured providers */
  async healthCheckAll(): Promise<Map<ProviderName, boolean>> {
    const results = new Map<ProviderName, boolean>();
    for (const [name, provider] of this.providers) {
      results.set(name, await provider.healthCheck());
    }
    return results;
  }
}
