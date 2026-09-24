Given your CPU-only setup (Intel i7-13620H) and severe RAM bottleneck (16GB single-channel DDR5), your benchmarking strategy must favor aggressively downsampled datasets and automated structural scoring. Running heavy image token weights or running models concurrently on a single-channel memory bus will saturate your memory bandwidth, crippling your tokens-per-second (t/s).
Here are the direct answers to your 4 core architectural and execution questions:
------------------------------
## 📋 Direct Answers to Your Clarifying Questions## 1. Concurrency Limit: Run 3 Small Models or Strictly Sequential?
Strictly sequential.
Your setup relies on a single 16GB stick. Single-channel RAM lacks the memory bandwidth (MT/s throughput channel) to feed parallel execution threads efficiently. If you attempt concurrent execution of 1.7B + 0.6B + 0.5B, your execution threads will violently compete for memory access cycles. This results in heavy context-switching overhead and catastrophic slowdowns. Run every screening test strictly sequential.
## 2. Test Images: Download Design2Code Now or Wait?
Download the primary datasets now, but filter down immediately.
You do not need to download the entirety of WebSight (which is massive). Instead, clone the official Design2Code GitHub Repository or pull down its primary evaluation split via Hugging Face. Focus strictly on extracting the first 30 to 50 entries from the test split to serve as your screening validation target.
## 3. Scoring Rubric: 1-5 Human Eval vs. Automated Pass/Fail?
Implement a Hybrid Automated Metric.
Human evaluation is too slow for cross-testing 18 runs per model across multiple candidates. Use an automated, lightweight multi-tiered scoring script:

   1. Syntactic Pass/Fail: A regex/parser check ensuring the model outputs closed HTML/CSS text structures without clipping due to token limit constraints.
   2. Structural Tree Matching: Parse the generated code and the original code using Python's BeautifulSoup to calculate an abstract syntax tree (AST) matching score (ignoring whitespace and minor class arrangements).
   3. Visual Delta (For Top 3 Deep Dive Only): Use a headless Chromium instance via [Playwright python](https://playwright.dev/python/) combined with the [pixelmatch](https://github.com/mapbox/pixelmatch) library to compute visual differences.

## 4. Experimental Models: Include super-coder Now or Defer?
Include it in Phase 3 screening.
Since it is a 4B parameter model distilled down from Claude, its spatial UI layout compliance under heavy quantization (Q4_0) will reveal whether code-specific distillation harms or preserves vision-language orientation.
------------------------------
## 🛠️ Strategic Breakdown for gcca_context.md Questions## 1. Dataset Sampling Strategy

* 
* Design2Code & WebSight: Download the parquet files of the [Hugging Face WebSight-Size-10k](https://huggingface.co/datasets/HuggingFaceM4/WebSight) subset instead of the full multi-terabyte original set. Write a short Python utility using pandas to isolate 10 landing pages, 10 forms, 10 dashboards, and 10 basic informational layouts using string tags matching text elements within the source HTML columns.
* DesignBench Frameworks: DesignBench evaluation parameters heavily lean on modern visual utility layers like Tailwind CSS. Ensure your prompt engineering instructions tell the model to explicitly format output using CDN-linked Tailwind stylesheets.
* 

## 2. Local Constraints & Prompt Engineering

* 
* Image Token Budgets: Keep your image inputs bound to 448×448 pixel caps. Forcing Qwen3-VL to read uncompressed 1080p full-page UI captures will cause its internal dynamic patch allocation to spike image token counts beyond 1,200 tokens. This will rapidly push your 8192 context window to its breaking point on your 16GB memory space.
* The VL Prompt Structure: For local low-quantization models like Qwen3-VL-4B-Instruct, avoid open-ended prompt targets. Use an explicit system script framework:
* 

You are an expert front-end developer. Analyze the provided UI mockup screenshot. 
Generate a single, completely self-contained HTML5 file including embedded CSS using Tailwind CSS classes via standard CDN links. 
Do not write explanations. Do not use markdown code block wrappers. Output only raw code.

To optimize the automated pipeline script, would you like me to generate a Python-based automated pipeline template that leverages Playwright and BeautifulSoup to run your model outputs directly against the benchmark's reference styles?


