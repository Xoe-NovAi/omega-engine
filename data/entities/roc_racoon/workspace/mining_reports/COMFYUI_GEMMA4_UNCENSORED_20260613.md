<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🦝 MINING REPORT: ComfyUI & Gemma 4 Uncensored - 2026-06-13

## 🎯 Overview
Analysis of a local-first multimodal pipeline using ComfyUI and an uncensored version of Gemma 4 for vision-to-prompt generation.

## 🔍 Technical Breakdown

### 1. The Stack
- **Orchestrator**: ComfyUI (Node-based visual graph).
- **Inference Backend**: Ollama (Local API server).
- **Model**: Gemma 4 "Aggressive" (by Frederzones 55) - Q4_K_M quantization.
- **Bridge**: ComfyUI-Ollama custom nodes.

### 2. The Workflow
- **Vision-to-Prompt**: Uses Gemma 4's vision capabilities to analyze a reference image.
- **Prompt Optimization**: A custom system prompt cleans the raw description into a high-density prompt for image generators (Flux/Zed).
- **Closed Loop**: The output of the LLM is fed directly into the positive prompt of the image generation node.

### 3. Sovereign Optimizations
- **VRAM Zero-Latency**: Setting `keep_alive=0` in Ollama to unload the LLM immediately after generation, preventing VRAM contention with the image model.
- **Censorship Bypass**: Use of "Aggressive" fine-tunes to ensure zero refusal for creative/NSFW content.

## 🛠️ Omega Engine Mapping
- **P6 (Cognition)**: This is a prime example of a multimodal perception $\rightarrow$ technical spec translation.
- **Sovereign Infrastructure**: Maps to our Local-First mandate (M7).
- **Potential Integration**: Implement a "Vision-to-Spec" pipeline within the Omega Orchestrator to automate prompt engineering for local image generators.
