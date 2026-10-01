<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Architectural Verification and Technical Integration Report for OpenCode CLI Configurations

## Plugin Interception Scope and Namespace Isolation

An architectural conflict in the OpenCode CLI ecosystem arises when using the opencode-antigravity-auth plugin alongside native provider configurations<sup>1</sup>. The plugin intercepts network calls at the runtime level to route requests through Google's internal Antigravity IDE infrastructure<sup>2</sup>.

Source code analysis of src/plugin/plugin.ts and src/plugin/request.ts reveals that the plugin implements global fetch() interception across the Node.js runtime<sup>3</sup>. The underlying validation function, isGenerativeLanguageRequest(), evaluates whether the target request URL string includes generativelanguage.googleapis.com<sup>3</sup>. This evaluation operates on a domain-wide string match rather than filtering by specific model identifiers or request payload metadata<sup>3</sup>.

When the interception hook monkey-patches the global fetch() transport layer, any model configured under the google provider namespace that targets generativelanguage.googleapis.com is intercepted<sup>3</sup>. If a user attempts to invoke a standard Google API model (such as google/gemini-2.5-pro using a native GEMINI_API_KEY), the plugin captures the request and replaces standard authorization headers with Antigravity OAuth tokens<sup>2</sup>. This substitution causes HTTP 403 Forbidden or authorization scope errors because standard API credentials are incompatible with internal Cloud AI Companion endpoints<sup>2</sup>.

Therefore, active installation of opencode-antigravity-auth hijacks the entire google provider namespace<sup>1</sup>. Standard Google API models inevitably break when the plugin is active under the google provider ID<sup>1</sup>.

Furthermore, the repository NoeFabris/opencode-antigravity-auth was archived on July 17, 2026, transitioning the codebase to read-only status<sup>7</sup>. Automated security systems on Google Cloud platforms have issued account suspensions to developer accounts utilizing unauthorized OAuth client IDs extracted from Antigravity binaries, making strict isolation of this plugin essential for operational stability and risk management<sup>9</sup>.

| **Inspection Parameter** | **Plugin Interception Behavior**                                           | **Native Google Provider Impact**                                              |
| ------------------------ | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Interception Hook Target | Global fetch() transport layer<sup>3</sup>                                 | All outgoing HTTP requests to Google AI endpoints<sup>3</sup>                  |
| ---                      | ---                                                                        | ---                                                                            |
| Matching Mechanism       | Substring match on generativelanguage.googleapis.com<br><br>\[cite: 3, 5\] | Model ID is ignored during interception routing<sup>3</sup>                    |
| ---                      | ---                                                                        | ---                                                                            |
| Credential Injection     | Overwrites x-goog-api-key with Antigravity OAuth tokens<sup>3</sup>        | Native Google API keys are stripped or ignored<sup>3</sup>                     |
| ---                      | ---                                                                        | ---                                                                            |
| Endpoint Target          | Reroutes calls to cloudaicompanion.googleapis.com<br><br>\[cite: 2, 6\]    | Standard API endpoints become unreachable under google namespace<sup>2</sup>   |
| ---                      | ---                                                                        | ---                                                                            |
| Provider Breakage        | **YES** - Complete namespace capture<sup>1</sup>                           | Standard Google API models fail with HTTP 403 / OAuth scope errors<sup>1</sup> |
| ---                      | ---                                                                        | ---                                                                            |

## Custom Provider Aliasing and TUI Credential Management Mechanics

To bypass namespace capture by opencode-antigravity-auth while retaining standard Google Gemini API access, OpenCode supports custom provider aliasing<sup>1</sup>. By establishing a secondary provider key (such as google-standard) that references the official @ai-sdk/google NPM package, the CLI instantiates an isolated provider instance<sup>11</sup>.

OpenCode's internal provider resolution in packages/opencode/src/provider/provider.ts distinguishes between built-in canonical loader keys and custom aliases<sup>13</sup>. Canonical providers (like google) invoke dedicated initialization routines, whereas custom provider identifiers (like google-standard) trigger the fallback SDK resolver<sup>13</sup>. This fallback resolver dynamically imports the declared package (@ai-sdk/google) and instantiates it via the package's factory method (createGoogle)<sup>13</sup>.

Because the alias google-standard does not match the hijacked google namespace, the plugin's interceptor does not interfere with the custom provider's execution pipeline unless the endpoint URL explicitly collides with intercepted domains<sup>3</sup>.

Credential storage in OpenCode is strictly partitioned by provider identifier within ~/.local/share/opencode/auth.json (or platform-equivalent XDG data paths)<sup>14</sup>. The workflow proceeds through clear operational steps:

- Execution of the Terminal User Interface (TUI) /connect command prompts the user for a target provider identifier<sup>14</sup>.
- Supplying google-standard creates a discrete dictionary entry in auth.json, stored explicitly under auth.json\["google-standard"\] with its corresponding API key<sup>14</sup>.
- The underlying server merges these stored credentials into the custom provider's runtime configuration, supplying apiKey directly to @ai-sdk/google during invocation<sup>14</sup>.

A secondary google-standard provider configured with @ai-sdk/google functions seamlessly alongside a plugin-hijacked google provider, maintaining separate TUI credential storage and independent network execution paths<sup>1</sup>.

| **Configuration Layer** | **google Namespace (Antigravity)**                                  | **google-standard Namespace (Native API)**                               |
| ----------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Driver Package          | opencode-antigravity-auth plugin<sup>2</sup>                        | @ai-sdk/google<br><br>\[cite: 11, 12\]                                   |
| ---                     | ---                                                                 | ---                                                                      |
| Auth Endpoint           | OAuth 2.0 via cloudaicompanion.googleapis.com<br><br>\[cite: 2, 6\] | REST / gRPC via generativelanguage.googleapis.com<br><br>\[cite: 3, 12\] |
| ---                     | ---                                                                 | ---                                                                      |
| TUI Auth Storage Key    | auth.json\["google"\]<br><br>\[cite: 15, 17\]                       | auth.json\["google-standard"\]<br><br>\[cite: 14, 15\]                   |
| ---                     | ---                                                                 | ---                                                                      |
| Interception Scope      | Intercepts and transforms outgoing payloads<sup>3</sup>             | Standard SDK transmission without transformation<sup>13</sup>            |
| ---                     | ---                                                                 | ---                                                                      |
| Operational Status      | Active via Antigravity OAuth quota pool<sup>2</sup>                 | Active via native Gemini API key<sup>12</sup>                            |
| ---                     | ---                                                                 | ---                                                                      |

## Gemma 4 Thinking Parameter Regressions and Client-Side Mitigation

An architectural issue with Google's Gemma 4 model series (specifically gemma-4-31b-it and gemma-4-26b-a4b-it) involves thinking parameter handling across API and local inference backends<sup>18</sup>.

Google Gemma Cookbook Issue #1198 details that setting generationConfig.thinkingConfig.includeThoughts: false on the v1beta API endpoint (generativelanguage.googleapis.com) is accepted without returning an HTTP 400 error, but is silently ignored by the server<sup>18</sup>. The returned JSON response continues to contain candidate parts marked with "thought": true<sup>18</sup>. In simple prompts, thought tokens routinely account for 85% to 95% of total generated candidate tokens, leading to unnecessary token billing and latency<sup>18</sup>. Because includeThoughts: false is a silent no-op at the API layer, client applications expecting suppressed reasoning payloads receive full thought channels<sup>18</sup>.

In OpenCode CLI (Issues #21034 and #21746), Gemma 4 integration failures manifest when running via local inference servers such as LM Studio or llama.cpp<sup>19</sup>. When OpenCode transmits tool schemas or prompt histories to local Gemma 4 instances, the engine fails to strip or isolate reasoning tags properly, causing the model to enter infinite tool-calling loops or omit tool arguments entirely<sup>19</sup>. Furthermore, OpenCode historically force-injected reasoning configuration structures into API payloads without verifying provider compatibility flags (capabilities.reasoning)<sup>1</sup>.

Client-side remediation requires explicitly configuring thinkingLevel: "MINIMAL" within the model's configuration variants<sup>1</sup>. Setting includeThoughts: false remains broken at the upstream API layer<sup>18</sup>. Declaring thinkingLevel: "MINIMAL" instructs the client runtime to request the lowest supported reasoning budget, suppressing thought token output to the minimum allowable threshold and preventing tool loop state corruption<sup>1</sup>.

| **Problem Layer**         | **Root Cause**                                                   | **Symptom / Failure Mode**                                               | **Verified Workaround**                                          |
| ------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Upstream Google API       | includeThoughts: false ignored in API v1beta<br><br>\[cite: 18\] | Thought tokens generated and billed (85-95% token overhead)<sup>18</sup> | Configure thinkingLevel: "MINIMAL"<br><br>\[cite: 1\]            |
| ---                       | ---                                                              | ---                                                                      | ---                                                              |
| OpenCode Client Core      | Force-injection of thinking parameters<sup>1</sup>               | Malformed requests sent to non-reasoning endpoints<sup>1</sup>           | Override model variants in opencode.json<br><br>\[cite: 1\]      |
| ---                       | ---                                                              | ---                                                                      | ---                                                              |
| Local Runners (LM Studio) | Tokenizer handling of Gemma 4 thought channels<sup>19</sup>      | Tool loops, repeated reads, context loss<sup>19</sup>                    | Update local llama.cpp engine & set MINIMAL thinking<sup>1</sup> |
| ---                       | ---                                                              | ---                                                                      | ---                                                              |

## OpenCode V2 Configuration Schema Evolution and Backward Compatibility

The OpenCode configuration system underwent a schema evolution in V2, refactoring how providers, models, options, and agents are represented<sup>1</sup>.

| **Schema Feature**     | **V1 Schema Specification**                             | **V2 Schema Specification**                            | **Operational Impact**                                                             |
| ---------------------- | ------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| Model Identifier Key   | Top-level object key or modelID<br><br>\[cite: 1\]      | Nested api.id property inside model object<sup>1</sup> | Allows display names to differ from API model IDs<sup>12</sup>                     |
| ---                    | ---                                                     | ---                                                    | ---                                                                                |
| Provider Settings      | Flat object properties alongside models<sup>1</sup>     | Explicit options wrapper object<sup>1</sup>            | Encapsulates baseURL, headers, and apiKey<br><br>\[cite: 22, 23\]                  |
| ---                    | ---                                                     | ---                                                    | ---                                                                                |
| Model Variants         | Key-value object mapping budget names<sup>1</sup>       | Explicit array of variant structures<sup>1</sup>       | Standardizes effort levels across agents<sup>1</sup>                               |
| ---                    | ---                                                     | ---                                                    | ---                                                                                |
| Modality Declaration   | Implied via hardcoded SDK capability flags<sup>24</sup> | Explicit modalities block in model entry<sup>24</sup>  | **Required for vision/multimodal support on custom providers**<br><br>\[cite: 24\] |
| ---                    | ---                                                     | ---                                                    | ---                                                                                |
| Backward Compatibility | Native baseline execution                               | V1 configurations normalized at boot                   | V1 flat configs continue to work via translation layer<sup>12</sup>                |
| ---                    | ---                                                     | ---                                                    | ---                                                                                |

V1-style configurations (flat variant definitions without an explicit options wrapper) remain functional in the OpenCode CLI due to internal schema translation functions executed during configuration boot<sup>12</sup>. However, custom provider declarations using @ai-sdk/openai-compatible require explicit modalities configuration in V2<sup>24</sup>.

Without explicitly declaring input and output modalities-such as specifying text and image inputs within modalities.input-OpenCode defaults capabilities.input.image to false for all non-canonical custom providers<sup>24</sup>. Consequently, vision and multimodal payload inputs are stripped prior to API dispatch unless explicitly configured<sup>24</sup>.

## Multi-Tier Configuration Merging Mechanics

OpenCode executes a deterministic, multi-tiered configuration loading and merging process across project environments<sup>26</sup>. The runtime aggregates settings from six distinct configuration locations, ordered from highest to lowest precedence:

1. OPENCODE_CONFIG_CONTENT: Ephemeral runtime environment variable overrides<sup>26</sup>.
2. .opencode/opencode.json: Local directory and IDE-specific subdirectory configurations<sup>26</sup>.
3. opencode.json: Project root configuration file<sup>26</sup>.
4. OPENCODE_CONFIG: Custom file path defined by environment variables<sup>26</sup>.
5. ~/.config/opencode/opencode.json: Global user-level configuration file<sup>26</sup>.
6. .well-known/opencode: Remote organizational defaults<sup>26</sup>.

The underlying merge function, mergeConfigConcatArrays(), located in packages/opencode/src/config/config.ts, governs how disparate JSON objects consolidate across these tiers<sup>26</sup>:

- **Objects**: Deep-merged recursively. Key collisions are resolved in favor of the higher-precedence configuration source<sup>1</sup>.
- **Arrays**: Concatenated sequentially. Array elements from higher-precedence files (such as plugin lists or custom command definitions) are appended to lower-precedence arrays rather than overwriting them<sup>1</sup>.
- **Scalars**: Directly overwritten by higher-precedence values<sup>1</sup>.

A project-level opencode.json correctly overrides scalar model parameters (such as limit.context or options.baseURL) defined in the global ~/.config/opencode/opencode.json, while augmenting the global model catalog with project-specific entries<sup>1</sup>.

An edge case documented in Issue #21307 affected nested .opencode/ directories, where filesystem traversal previously inverted precedence by applying parent directory overrides over child directory configs<sup>27</sup>. This regression was addressed in subsequent releases by enforcing root-first traversal during file discovery<sup>27</sup>.

| **Configuration Scope** | **Path Location**                       | **Merge Priority**   | **Primary Architectural Function**                                |
| ----------------------- | --------------------------------------- | -------------------- | ----------------------------------------------------------------- |
| Environment Inline      | OPENCODE_CONFIG_CONTENT env var         | Priority 1 (Highest) | Ephemeral runtime overrides for CI/CD pipelines<sup>26</sup>      |
| ---                     | ---                                     | ---                  | ---                                                               |
| Local Subdirectory      | &lt;project&gt;/.opencode/opencode.json | Priority 2           | IDE-specific plugin & agent settings<sup>26</sup>                 |
| ---                     | ---                                     | ---                  | ---                                                               |
| Project Root            | &lt;project&gt;/opencode.json           | Priority 3           | Project-specific model overrides and local endpoints<sup>26</sup> |
| ---                     | ---                                     | ---                  | ---                                                               |
| Global User             | ~/.config/opencode/opencode.json        | Priority 5           | Global API keys, default providers, primary catalog<sup>26</sup>  |
| ---                     | ---                                     | ---                  | ---                                                               |
| Remote Default          | .well-known/opencode                    | Priority 6 (Lowest)  | Enterprise governance and baseline defaults<sup>26</sup>          |
| ---                     | ---                                     | ---                  | ---                                                               |

## Multi-Provider Failover Architecture and Circuit Breaking

OpenCode incorporates an automated provider failover and rate-limit mitigation framework designed to maintain agent execution during upstream provider outages<sup>1</sup>. The failover engine evaluates HTTP status codes returned during inference streaming<sup>3</sup>:

- **HTTP 429 (Rate Limit Exceeded)**: Triggers account rotation if multi-account OAuth is active, or immediately shifts execution to the next provider in the configured fallback chain<sup>3</sup>.
- **HTTP 500 / 502 / 503 (Upstream Server Error)**: Triggers an endpoint cascade across fallback URLs before failing over to secondary providers<sup>3</sup>.
- **HTTP 403 (Forbidden / Auth Error)**: Indicates credential revocation or header mismatch (such as problematic x-goog-user-project headers), initiating immediate circuit breaking on the affected provider<sup>6</sup>.

To maximize availability while minimizing operational costs, the optimal provider fallback chain progresses through six distinct priority tiers:

1. native-gguf: Embedded local models providing zero-cost, offline fallback capabilities<sup>1</sup>.
2. lmstudio: Local GPU inference server handling higher-parameter models without API charges<sup>1</sup>.
3. opencode (Zen): Free cloud inference tier offering high-speed models like MiMo v2.5 and Nemotron 3 Ultra<sup>1</sup>.
4. antigravity: OAuth-based IDE quota pool providing access to frontier reasoning models<sup>1</sup>.
5. google-standard: Direct, paid Google Gemini API tier ensuring reliable paid execution<sup>1</sup>.
6. openrouter: Multi-provider aggregator serving as the final global backstop for model availability<sup>1</sup>.

| **Fallback Order** | **Provider Identifier** | **Target Capability**     | **Cost Profile**               | **Failover Rationale**                                       |
| ------------------ | ----------------------- | ------------------------- | ------------------------------ | ------------------------------------------------------------ |
| 1                  | native-gguf             | Embedded local models     | Free (Zero network dependency) | Instant local execution, offline backup<sup>1</sup>          |
| ---                | ---                     | ---                       | ---                            | ---                                                          |
| 2                  | lmstudio                | Local GPU server          | Free (Zero API cost)           | Higher parameter local models (Gemma 4 / Qwen 3)<sup>1</sup> |
| ---                | ---                     | ---                       | ---                            | ---                                                          |
| 3                  | opencode (Zen)          | Free cloud inference      | Free (Rate-limited tier)       | High-speed cloud models (MiMo v2.5, Nemotron)<sup>1</sup>    |
| ---                | ---                     | ---                       | ---                            | ---                                                          |
| 4                  | antigravity             | OAuth IDE quota           | Free (OAuth rate limits)       | Claude Opus 4.6 Thinking & Gemini 3.1 Pro<sup>1</sup>        |
| ---                | ---                     | ---                       | ---                            | ---                                                          |
| 5                  | google-standard         | Native Gemini API         | Paid (Pay-per-token API)       | Direct Google API, highly reliable paid tier<sup>1</sup>     |
| ---                | ---                     | ---                       | ---                            | ---                                                          |
| 6                  | openrouter              | Multi-provider aggregator | Paid / Free catch-all          | Final global backstop for model availability<sup>1</sup>     |
| ---                | ---                     | ---                       | ---                            | ---                                                          |

## Model Identifier Conventions, Parsing Rules, and Interface Rendering

OpenCode enforces a strict canonical naming convention for referencing models within terminal environments and configuration files<sup>1</sup>. The primary syntax follows the format provider_id/model_id<sup>1</sup>.

During invocation or configuration parsing, OpenCode splits the model string at the **first forward slash (/)**<sup>1</sup>. The substring preceding the first slash is extracted as the provider_id, and the remainder is passed to the provider SDK as the internal model_id<sup>1</sup>. For example, in the model string openrouter/google/gemma-4, openrouter is extracted as the provider ID, and google/gemma-4 is passed as the internal model ID<sup>1</sup>.

A technical edge case occurs when integration providers (such as Groq or OpenRouter) require model identifiers that themselves contain forward slashes, such as groq/moonshotai/kimi-k2-instruct-0905<sup>21</sup>. If a user requests groq/moonshotai/kimi-k2-instruct-0905 without explicit configuration, OpenCode extracts groq as the provider ID and transmits moonshotai/kimi-k2-instruct-0905 to the Groq API<sup>21</sup>. If the provider API expects the full prefixed identifier or a specific alias, the request fails<sup>21</sup>.

To resolve nested slash conflicts, model entries in opencode.json must explicitly define the internal id property inside the model configuration<sup>21</sup>. Defining id explicitly ensures that the exact string required by the upstream API is transmitted, while the top-level configuration key serves as the local handle<sup>21</sup>.

The name key explicitly controls the visual rendering string displayed in the TUI model selection menu, preventing long upstream IDs from cluttering the terminal interface<sup>12</sup>.

## Comprehensive Provider Catalogs, Technical Specifications, and Protocol Regressions

### Google Antigravity Model Catalog

The Antigravity provider operates via OAuth authorization against Google's Cloud AI Companion infrastructure<sup>2</sup>. While offering access to frontier models, it presents risk factors regarding Terms of Service compliance and account longevity<sup>9</sup>.

| **Model Identifier**                        | **Display Name**             | **Context Window** | **Output Limit** | **Supported Thinking Config**                  | **Known Issues & Protocol Regressions**                               |
| ------------------------------------------- | ---------------------------- | ------------------ | ---------------- | ---------------------------------------------- | --------------------------------------------------------------------- |
| google/antigravity-gemini-3.1-pro           | Gemini 3.1 Pro (Antigravity) | 1,048,576          | 65,536           | thinkingLevel (MINIMAL, LOW, HIGH)<sup>7</sup> | Identity mismatch in multi-turn conversations<sup>1</sup>             |
| ---                                         | ---                          | ---                | ---              | ---                                            | ---                                                                   |
| google/antigravity-gemini-3-flash           | Gemini 3 Flash (Antigravity) | 1,048,576          | 8,192            | Not supported                                  | Quota throttling during peak execution hours                          |
| ---                                         | ---                          | ---                | ---              | ---                                            | ---                                                                   |
| google/antigravity-claude-opus-4-6-thinking | Claude Opus 4.6 Thinking     | 200,000            | 32,768           | thinkingBudget (Max Variant)<sup>2</sup>       | Thought signature stripping required in request.ts<br><br>\[cite: 3\] |
| ---                                         | ---                          | ---                | ---              | ---                                            | ---                                                                   |
| google/antigravity-claude-sonnet-4-6        | Claude Sonnet 4.6            | 200,000            | 16,384           | Disabled                                       | Requires JSON schema cleaning (strips \$ref, const)<sup>3</sup>       |
| ---                                         | ---                          | ---                | ---              | ---                                            | ---                                                                   |
| google/antigravity-nano-banana-2            | Nano Banana 2                | 128,000            | 4,096            | Native image grounding<sup>33</sup>            | Experimental status; potential payload schema rejection               |
| ---                                         | ---                          | ---                | ---              | ---                                            | ---                                                                   |

Community reports on the Google AI Developers Forum document account suspensions resulting from automated detection of non-IDE OAuth signatures<sup>9</sup>. Utilizing dedicated development accounts isolated from primary Google Workspace services is strongly advised<sup>10</sup>.

### OpenRouter Free Tier Catalog

OpenRouter provides a rotating selection of zero-cost models subject to global rate limits<sup>34</sup>.

| **Model Identifier**                              | **Context Window** | **Output Cap** | **Default Rate Limits**      | **Upstream Routing & Cap Notes**                              |
| ------------------------------------------------- | ------------------ | -------------- | ---------------------------- | ------------------------------------------------------------- |
| openrouter/meta-llama/llama-3.3-70b-instruct:free | 131,072            | 8,192          | 20 RPM / 50 RPD<sup>34</sup> | Increases to 1,000 RPD if account balance > \$10<sup>35</sup> |
| ---                                               | ---                | ---            | ---                          | ---                                                           |
| openrouter/deepseek/deepseek-r1:free              | 163,840            | 8,192          | 20 RPM / 50 RPD<sup>34</sup> | High demand causes periodic HTTP 503 backoff                  |
| ---                                               | ---                | ---            | ---                          | ---                                                           |
| openrouter/qwen/qwen-2.5-coder-32b-instruct:free  | 32,768             | 4,096          | 20 RPM / 50 RPD<sup>34</sup> | Fast execution; ideal for lightweight code edits              |
| ---                                               | ---                | ---            | ---                          | ---                                                           |
| openrouter/google/gemini-2.5-flash:free           | 1,048,576          | 8,192          | 20 RPM / 50 RPD<sup>34</sup> | Routes through AI Studio free endpoints<sup>1</sup>           |
| ---                                               | ---                | ---            | ---                          | ---                                                           |

### OpenCode Zen Tier Catalog

OpenCode Zen provides high-performance models maintained directly by the OpenCode core team<sup>1</sup>.

| **Model Identifier**       | **Display Name**      | **Context Window** | **Output Limit** | **Availability Tier** | **Technical Notes**                                        |
| -------------------------- | --------------------- | ------------------ | ---------------- | --------------------- | ---------------------------------------------------------- |
| opencode/mimo-v2.5         | MiMo v2.5 Free        | 200,000            | 16,384           | Free                  | Native coding variant; high tool call accuracy<sup>1</sup> |
| ---                        | ---                   | ---                | ---              | ---                   | ---                                                        |
| opencode/nemotron-3-ultra  | Nemotron 3 Ultra Free | 1,048,576          | 128,000          | Free                  | Massive output budget; ideal for refactoring<sup>1</sup>   |
| ---                        | ---                   | ---                | ---              | ---                   | ---                                                        |
| opencode/claude-sonnet-4-5 | Claude Sonnet 4.5     | 200,000            | 16,384           | Zen Paid Subscription | Optimized prompt caching via Zen Gateway                   |
| ---                        | ---                   | ---                | ---              | ---                   | ---                                                        |
| opencode/gpt-5.2           | GPT-5.2 Turbo         | 128,000            | 16,384           | Zen Paid Subscription | Strict JSON schema compliance                              |
| ---                        | ---                   | ---                | ---              | ---                   | ---                                                        |

### Cerebras Infrastructure Catalog and Known Regressions

Cerebras offers high-speed wafer-scale inference but exhibits distinct protocol edge cases within OpenCode<sup>36</sup>.

| **Model Identifier**       | **Drivers / Package**                         | **Context Limit** | **Rate Limit (TPM)** | **Known Issues & Regressions**                                                                                                                                                                                                                            |
| -------------------------- | --------------------------------------------- | ----------------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| cerebras/zai-glm-4.7       | @ai-sdk/cerebras<br><br>\[cite: 36\]          | 131,072           | 500,000<sup>37</sup> | **Issue #26762**: Multi-turn reasoning replay fails with messages.assistant.reasoning_content unsupported (fixed in v1.17.14)<sup>38</sup>. **Issue #10851**: Token accounting reports up to 15x inflated usage due to cached token billing<sup>37</sup>. |
| ---                        | ---                                           | ---               | ---                  | ---                                                                                                                                                                                                                                                       |
| cerebras/qwen-3-coder-480b | @ai-sdk/cerebras<br><br>\[cite: 36\]          | 65,536            | 500,000<sup>37</sup> | High speed (>1800 t/s); requires explicit API key configuration due to autoload: false setting<sup>39</sup>.                                                                                                                                              |
| ---                        | ---                                           | ---               | ---                  | ---                                                                                                                                                                                                                                                       |
| cerebras/gpt-oss-120b      | @ai-sdk/openai-compatible<br><br>\[cite: 36\] | 131,072           | 500,000<sup>37</sup> | Legacy builds threw body.maxTokens unsupported (resolved in v1.1.1)<sup>40</sup>.                                                                                                                                                                         |
| ---                        | ---                                           | ---               | ---                  | ---                                                                                                                                                                                                                                                       |

### Groq Cloud Catalog and Protocol Specifications

Groq provides LPPU-accelerated inference requiring specific model mapping rules for multi-slash IDs<sup>21</sup>.

| **Model Identifier** | **Upstream API ID**                                  | **Context Limit** | **Rate Limit**           | **Configuration Requirement**                                                                                       |
| -------------------- | ---------------------------------------------------- | ----------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| groq/kimi-k2         | moonshotai/kimi-k2-instruct-0905<br><br>\[cite: 31\] | 131,072           | 250,000 TPM<sup>31</sup> | **Must declare id: "moonshotai/kimi-k2-instruct-0905"** in model config to prevent provider stripping<sup>21</sup>. |
| ---                  | ---                                                  | ---               | ---                      | ---                                                                                                                 |
| groq/compound        | groq/compound<br><br>\[cite: 21\]                    | 128,000           | 1,000 RPM                | Requires full ID prefix retention in API payload<sup>21</sup>.                                                      |
| ---                  | ---                                                  | ---               | ---                      | ---                                                                                                                 |
| groq/llama-3.3-70b   | llama-3.3-70b-versatile                              | 128,000           | 300,000 TPM              | Standard OpenAI-compatible driver mapping<sup>21</sup>.                                                             |
| ---                  | ---                                                  | ---               | ---                      | ---                                                                                                                 |

## Master Configuration Specifications

To establish a verified OpenCode deployment that isolates the opencode-antigravity-auth plugin, resolves the Gemma 4 thinking bug, enables standard Google API access, and provides a multi-tier fallback architecture, deploy the following three configuration files.

### 1\. Global User Configuration (~/.config/opencode/opencode.json)

JSON

{  
"\$schema": "<https://opencode.ai/config.json>",  
"plugin": \[  
"opencode-antigravity-auth@latest"  
\],  
"provider": {  
"google": {  
"npm": "@ai-sdk/google",  
"models": {  
"antigravity-claude-opus-4-6-thinking": {  
"name": "Claude Opus 4.6 Thinking (Antigravity)",  
"limit": {  
"context": 200000,  
"output": 32768  
}  
},  
"antigravity-gemini-3.1-pro": {  
"name": "Gemini 3.1 Pro (Antigravity)",  
"limit": {  
"context": 1048576,  
"output": 65536  
}  
}  
}  
},  
"google-standard": {  
"npm": "@ai-sdk/google",  
"options": {  
"apiKey": "{env:GEMINI_API_KEY}"  
},  
"models": {  
"gemini-2.5-pro": {  
"id": "gemini-2.5-pro",  
"name": "Gemini 2.5 Pro (Direct API)",  
"limit": {  
"context": 1048576,  
"output": 65536  
}  
},  
"gemini-2.5-flash": {  
"id": "gemini-2.5-flash",  
"name": "Gemini 2.5 Flash (Direct API)",  
"limit": {  
"context": 1048576,  
"output": 8192  
}  
}  
}  
},  
"lmstudio": {  
"npm": "@ai-sdk/openai-compatible",  
"options": {  
"baseURL": "<http://localhost:1234/v1>"  
},  
"models": {  
"gemma-4-26b-a4b-it": {  
"name": "Gemma 4 26B Local (LM Studio)",  
"limit": {  
"context": 65536,  
"output": 8192  
},  
"modalities": {  
"input": \["text", "image"\],  
"output": \["text"\]  
},  
"options": {  
"thinkingLevel": "MINIMAL"  
}  
}  
}  
},  
"groq": {  
"npm": "@ai-sdk/openai-compatible",  
"options": {  
"baseURL": "<https://api.groq.com/openai/v1>",  
"apiKey": "{env:GROQ_API_KEY}"  
},  
"models": {  
"kimi-k2": {  
"id": "moonshotai/kimi-k2-instruct-0905",  
"name": "Groq Kimi K2 Instruct",  
"limit": {  
"context": 131072,  
"output": 8192  
}  
}  
}  
},  
"cerebras": {  
"npm": "@ai-sdk/cerebras",  
"options": {  
"apiKey": "{env:CEREBRAS_API_KEY}"  
},  
"models": {  
"zai-glm-4.7": {  
"name": "Cerebras GLM 4.7",  
"limit": {  
"context": 131072,  
"output": 8192  
}  
}  
}  
}  
}  
}

### 2\. Project Root Configuration (omega-engine/opencode.json)

JSON

{  
"\$schema": "<https://opencode.ai/config.json>",  
"provider": {  
"opencode": {  
"models": {  
"mimo-v2.5": {  
"name": "OpenCode Zen MiMo v2.5 (Free)",  
"limit": {  
"context": 200000,  
"output": 16384  
}  
},  
"nemotron-3-ultra": {  
"name": "OpenCode Zen Nemotron 3 Ultra (Free)",  
"limit": {  
"context": 1048576,  
"output": 128000  
}  
}  
}  
},  
"openrouter": {  
"npm": "@ai-sdk/openai-compatible",  
"options": {  
"baseURL": "<https://openrouter.ai/api/v1>",  
"apiKey": "{env:OPENROUTER_API_KEY}"  
},  
"models": {  
"llama-3.3-70b-free": {  
"id": "meta-llama/llama-3.3-70b-instruct:free",  
"name": "OpenRouter Llama 3.3 70B (Free)",  
"limit": {  
"context": 131072,  
"output": 8192  
}  
}  
}  
}  
}  
}

### 3\. Subdirectory Configuration (omega-engine/.opencode/opencode.json)

JSON

{  
"\$schema": "<https://opencode.ai/config.json>",  
"provider": {  
"google": {  
"models": {  
"antigravity-claude-opus-4-6-thinking": {  
"variants": {  
"max": {  
"thinkingBudget": 32768  
},  
"medium": {  
"thinkingBudget": 16384  
},  
"low": {  
"thinkingBudget": 4096  
}  
}  
},  
"antigravity-gemini-3.1-pro": {  
"variants": {  
"high": {  
"thinkingLevel": "HIGH"  
},  
"medium": {  
"thinkingLevel": "LOW"  
},  
"minimal": {  
"thinkingLevel": "MINIMAL"  
}  
}  
}  
}  
}  
}  
}

#### Works cited

1. R_OPENCODE_CONFIG_VERIFICATION_DIRECTIVE_20260809.md
2. Antigravity + Gemini CLI OAuth Plugin for Opencode - GitHub, <https://github.com/NoeFabris/opencode-antigravity-auth>
3. opencode-antigravity-auth/docs/ARCHITECTURE.md at main - GitHub, <https://github.com/NoeFabris/opencode-antigravity-auth/blob/main/docs/ARCHITECTURE.md>
4. refactor: Decompose monolithic request.ts into maintainable modules · Issue #101 · NoeFabris/opencode-antigravity-auth - GitHub, <https://github.com/NoeFabris/opencode-antigravity-auth/issues/101>
5. Getting the error: models/antigravity-claude-opus-4-5-thinking is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods · Issue #303 - GitHub, <https://github.com/NoeFabris/opencode-antigravity-auth/issues/303>
6. Antigravity auth: 403s from stale headers, missing endpoint fallbacks, extra fingerprint headers · Issue #1830 · earendil-works/pi - GitHub, <https://github.com/earendil-works/pi/issues/1830>
7. Activity · NoeFabris/opencode-antigravity-auth - GitHub, <https://github.com/NoeFabris/opencode-antigravity-auth/activity>
8. \[BUG\] TypeError \[ERR_INVALID_URL\]: fetch() URL is invalid when using Antigravity models via oh-my-opencode #49 - GitHub, <https://github.com/NoeFabris/opencode-antigravity-auth/issues/49>
9. Account banned after using OpenCode OAuth plugin - Appeal Request - Google Antigravity, <https://discuss.ai.google.dev/t/account-banned-after-using-opencode-oauth-plugin-appeal-request/130898>
10. opencode-antigravity-auth - NPM, <https://www.npmjs.com/package/opencode-antigravity-auth?activeTab=versions>
11. NikkeTryHard/zerogravity: OpenAI, Anthropic, and Gemini-compatible proxy. - GitHub, <https://github.com/NikkeTryHard/zerogravity>
12. CC Hub Usage Documentation, <https://airoute.mycyjg.net/en/usage-doc>
13. Vertex AI provider can't run two regions in the same session #28524 - GitHub, <https://github.com/anomalyco/opencode/issues/28524>
14. Providers - OpenCode, <https://opencode.ai/docs/providers/>
15. \[FEATURE\]: multiple auth profiles per provider · Issue #5391 · anomalyco/opencode - GitHub, <https://github.com/anomalyco/opencode/issues/5391>
16. Have multiple instances of the same provider · Issue #6217 · anomalyco/opencode - GitHub, <https://github.com/anomalyco/opencode/issues/6217>
17. VSCode Extension: loadOpenCodeConfig() Only Loads 2 Providers (Ignores Google, GitHub Copilot, OpenRouter) · Issue #6066 · anomalyco/opencode, <https://github.com/anomalyco/opencode/issues/6066>
18. gemma-4-31b-it: thinkingConfig.includeThoughts: false is silently ignored, thought parts still returned · Issue #1198 · google-gemini/cookbook - GitHub, <https://github.com/google-gemini/cookbook/issues/1198>
19. gemma-4-26b and gemma-4-31b opencode interaction issues leading to tool loops/failures #21034 - GitHub, <https://github.com/anomalyco/opencode/issues/21034>
20. Gemma 4 26B does not think when used with opencode #21746 - GitHub, <https://github.com/anomalyco/opencode/issues/21746>
21. add support for groq compound (the model) · Issue #16213 · anomalyco/opencode - GitHub, <https://github.com/anomalyco/opencode/issues/16213>
22. Ollama Turbo Support #2467 - anomalyco/opencode - GitHub, <https://github.com/anomalyco/opencode/issues/2467>
23. local LAN provider discovery + auto-discover models by androidand · Pull Request #27554 · anomalyco/opencode - GitHub, <https://github.com/anomalyco/opencode/pull/27554>
24. docs: modalities field for custom provider models is undocumented · Issue #25228 · anomalyco/opencode - GitHub, <https://github.com/anomalyco/opencode/issues/25228>
25. Feature Request: Add Vercel AI Gateway Provider Routing Support (\`only\` and \`order\` filters) · Issue #2153 · anomalyco/opencode - GitHub, <https://github.com/anomalyco/opencode/issues/2153>
26. OPENCODE_CONFIG_CONTENT does not have highest precedence config loading · Issue #11628 · anomalyco/opencode - GitHub, <https://github.com/anomalyco/opencode/issues/11628>
27. \`.opencode/\` config precedence is inverted in nested directories · Issue #21307 · anomalyco/opencode - GitHub, <https://github.com/anomalyco/opencode/issues/21307>
28. theblazehen/opencode-antigravity-multi-auth - GitHub, <https://github.com/theblazehen/opencode-antigravity-multi-auth>
29. github.com/mark3labs/kit v0.79.2-0.20260618114603-bd56f4a089b0 on Go - Libraries.io - security & maintenance data for open source software, <https://libraries.io/go/github.com%2Fmark3labs%2Fkit>
30. Pricing - OpenRouter, <https://openrouter.ai/pricing>
31. Add Kimi K2 models to Groq provider · Issue #9135 · anomalyco/opencode - GitHub, <https://github.com/anomalyco/opencode/issues/9135>
32. Solution draft log for <https://github.com/link-assistant/agent/pull/202> · GitHub, <https://gist.github.com/konard/c9aa8a74ad6b263750d31f46352c2e90>
33. google-gemini/cookbook: Examples and guides for using the Gemini API - GitHub, <https://github.com/google-gemini/cookbook>
34. OpenRouter Free Models: All 15 Listed (Aug 2026) - CostGoat, <https://costgoat.com/pricing/openrouter-free-models>
35. OpenRouter Rate Limits - What You Need to Know, <https://openrouter.zendesk.com/hc/en-us/articles/39501163636379-OpenRouter-Rate-Limits-What-You-Need-to-Know>
36. <https://api.cerebras.ai/v1> --> UnknownError: AI_APICallError: Bad Request · Issue #1481 · anomalyco/opencode - GitHub, <https://github.com/anomalyco/opencode/issues/1481>
37. Very high input token usage with Cerebras (GLM 4.7) · Issue #10851 · anomalyco/opencode, <https://github.com/anomalyco/opencode/issues/10851>
38. Cerebras zai-glm-4.7 fails on follow-up turn with reasoning_content #26762 - GitHub, <https://github.com/anomalyco/opencode/issues/26762>
39. Cerebras models no longer found by opencode #10356 - GitHub, <https://github.com/anomalyco/opencode/issues/10356>
40. Using any cerebras model with api key causes unsupported property errors #6648 - GitHub, <https://github.com/anomalyco/opencode/issues/6648>