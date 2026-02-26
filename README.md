# 🧠 Multi-AI Council

A powerful CLI-based orchestrator that brings multiple AI "personas" together to debate, critique, and solve complex problems or review code. Instead of relying on a single AI's output, you get a synthesized perspective from a council of distinct experts who argue with each other to find the truth.

## 🏗️ Architecture: The 3-Round Workflow

The Multi-AI Council uses a strict **3-Round Workflow** to ensure diverse, thoroughly stress-tested answers. It features a **real-time streaming terminal UI**, meaning you watch the agents' answers stream in live as they finish thinking.

1. **Round 1 (Individual Analysis):**
   - The user's query or file is sent in parallel to multiple distinct AI Personas.
   - Each agent isolates themselves and answers independently based on their radically different system prompts.
2. **Round 2 (Cross-Critique):**
   - The Orchestrator compiles all Round 1 answers into a transcript.
   - This transcript is sent _back_ to every agent along with a specialized "Critique Prompt".
   - Agents are forced to read each other's answers to find flaws, point out groupthink, or challenge assumptions.
3. **Round 3 (Synthesis):**
   - "The Judge" Persona receives the original query, the independent answers from Round 1, and the spirited debate from Round 2.
   - The Judge synthesizes the best points, resolves conflicts, highlights critical warnings, and provides a final, actionable answer to the user.

## 🎭 The Personas

The magic of this tool lies in the rigidly defined personas. They are not designed to be polite; they are designed to find the best answer.

- 🔬 **The Scientist:** Rigorous, skeptical, and evidence-obsessed. Demands empirical justification for every claim and rejects buzzwords.
- 🎨 **The Creative:** Thinks sideways. Actively searches for non-obvious approaches and draws analogies from unrelated fields.
- 😈 **The Devil's Advocate:** Sole purpose is to find failure modes (security risks, race conditions, hidden costs). Blunt and adversarial.
- 🏗️ **The Pragmatist:** The production realist. Evaluates cloud bills, licensing, and maintainability. Ruthlessly flags over-engineering.
- 📚 **The Theorist:** The pattern expert. Evaluates problems through the lens of SOLID principles, CAP theorem, and 2-year architectural debt.
- ⚖️ **The Judge:** The final synthesizer. Condenses the debate into a final verdict, noting consensus, key conflicts, and an actionable roadmap.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) (For running local models completely free)
- _Optional:_ API Keys for OpenAI or Anthropic

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/multi-ai-council.git
   cd multi-ai-council
   ```

2. Create a virtual environment and activate it:

   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) If you want to use OpenAI or Anthropic, add your API keys to the `.env` file:
   ```env
   OPENAI_API_KEY="your-key-here"
   ANTHROPIC_API_KEY="your-key-here"
   ```

## 💻 Usage

Make sure your virtual environment is activated.

**Note for Windows Users:** Set your terminal encoding to UTF-8 to display emojis and complex formatting properly:

```powershell
$env:PYTHONIOENCODING="utf-8"
```

### Basic Prompt (Using Local Ollama)

By default, the CLI uses the `llama3.1:8b` model via Ollama. Make sure you have pulled it first (`ollama pull llama3.1:8b`).

```bash
python main.py --prompt "Is the Singleton pattern an anti-pattern? Explain why or why not."
```

### Reviewing a Code File

Instead of a prompt, pass a file for the entire council to review for architecture, bugs, and edge cases.

```bash
python main.py --file my_script.py
```

### Changing Providers & Models

You can run the council on different AI providers by using the `--provider` and `--model` flags. The council operates seamlessly across providers.

**Using OpenAI / ChatGPT:**

```bash
python main.py --file app.js --provider openai --model gpt-4-turbo
```

**Using Anthropic / Claude:**

```bash
python main.py --prompt "Review this architectural plan" --provider anthropic --model claude-3-5-sonnet-20240620
```

## 🛠️ Project Structure

- `main.py` - The CLI entry point and streaming UI logic.
- `core/orchestrator.py` - Contains the parallel processing `CouncilOrchestrator` that manages the 3-round workflow.
- `core/personas.py` - Defines the deep system prompts and critique rules for each AI agent.
- `core/llm/` - Abstracted interface to talk to Ollama, OpenAI, or Anthropic interchangeably.

## 🤝 Contributing

Feel free to open issues, submit Pull Requests, or suggest new Agent Personas. If you build a web UI for this, please link it!
