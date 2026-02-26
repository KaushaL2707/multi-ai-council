import concurrent.futures
from typing import List, Dict, Any
from .llm.base import BaseLLM
from .personas import Persona, PERSONAS


class CouncilOrchestrator:
    def __init__(self, llm_client: BaseLLM):
        self.llm = llm_client

    def run_round_1(self, user_prompt: str, agents: List[Persona], callback=None) -> Dict[str, str]:
        """Round 1: Each agent answers independently in parallel."""
        results = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(agents)) as executor:
            future_to_agent = {
                executor.submit(
                    self.llm.generate_response,
                    system_prompt=agent.system_prompt,
                    user_prompt=(
                        f"{user_prompt}\n\n"
                        f"INSTRUCTIONS: Respond strictly as {agent.name}. "
                        f"Be direct and specific. Max 300 words. No preamble."
                    )
                ): agent for agent in agents
            }

            for future in concurrent.futures.as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    response = future.result()
                    results[agent.name] = response
                    if callback:
                        callback(agent.name, response)
                except Exception as exc:
                    results[agent.name] = f"Error: {exc}"
                    if callback:
                        callback(agent.name, results[agent.name])

        return results

    def run_round_2(self, original_prompt: str, round_1_results: Dict[str, str], agents: List[Persona], callback=None) -> Dict[str, str]:
        """Round 2: Each agent critiques the others. Receives ONLY the other agents' Round 1 responses."""
        results = {}

        # Build a clean, compact transcript — no fluff
        transcript = ""
        for agent_name, response in round_1_results.items():
            # Truncate each response to ~400 chars to keep context tight
            truncated = response[:600] + "..." if len(response) > 600 else response
            transcript += f"[{agent_name}]: {truncated}\n\n"

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(agents)) as executor:
            future_to_agent = {}
            for agent in agents:
                round_2_prompt = (
                    f"ORIGINAL QUESTION: {original_prompt}\n\n"
                    f"=== ROUND 1: WHAT YOUR COLLEAGUES SAID ===\n"
                    f"{transcript.strip()}\n\n"
                    f"=== YOUR TASK ===\n"
                    f"You are {agent.name}. Do NOT repeat or summarize what others said.\n"
                    f"React to it. Challenge it. Find what's wrong or missing.\n"
                    f"Be specific — name the agent you're disagreeing with.\n"
                    f"Max 250 words. Stay in character."
                )
                future = executor.submit(
                    self.llm.generate_response,
                    system_prompt=agent.critique_prompt,
                    user_prompt=round_2_prompt
                )
                future_to_agent[future] = agent

            for future in concurrent.futures.as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    response = future.result()
                    results[agent.name] = response
                    if callback:
                        callback(agent.name, response)
                except Exception as exc:
                    results[agent.name] = f"Error: {exc}"
                    if callback:
                        callback(agent.name, results[agent.name])

        return results

    def run_round_3(self, original_prompt: str, round_1_results: Dict[str, str], round_2_results: Dict[str, str], judge: Persona) -> str:
        """Round 3: Judge synthesizes a clean structured verdict. Does NOT receive raw agent text."""

        # Build compact Round 1 summary (key points only, truncated)
        round_1_summary = ""
        for agent_name, response in round_1_results.items():
            truncated = response[:500] + "..." if len(response) > 500 else response
            round_1_summary += f"[{agent_name}]:\n{truncated}\n\n"

        # Build compact Round 2 summary
        round_2_summary = ""
        for agent_name, response in round_2_results.items():
            truncated = response[:400] + "..." if len(response) > 400 else response
            round_2_summary += f"[{agent_name} critique]:\n{truncated}\n\n"

        judge_prompt = (
            f"ORIGINAL QUESTION:\n{original_prompt}\n\n"
            f"=== ROUND 1: INITIAL POSITIONS ===\n"
            f"{round_1_summary.strip()}\n\n"
            f"=== ROUND 2: CRITIQUES & CONFLICTS ===\n"
            f"{round_2_summary.strip()}\n\n"
            f"=== YOUR JOB ===\n"
            f"You are The Judge. Based on the debate above, deliver your FINAL VERDICT.\n"
            f"Use ONLY the required structure. Do not quote agents verbatim.\n"
            f"You MUST pick a side on every conflict. No 'it depends' without resolution.\n"
            f"Be opinionated. Be concise. Every sentence must earn its place."
        )

        try:
            return self.llm.generate_response(
                system_prompt=judge.system_prompt,
                user_prompt=judge_prompt
            )
        except Exception as exc:
            return f"Judge error: {exc}"

    def run_council(self, user_prompt: str, agent_keys: List[str] = None, round_1_cb=None, round_2_cb=None) -> Dict[str, Any]:
        """Runs the full 3-round council workflow."""
        if agent_keys is None:
            agent_keys = ["scientist", "creative", "devil_advocate", "pragmatist"]

        active_agents = [PERSONAS[key] for key in agent_keys if key in PERSONAS]
        judge = PERSONAS["judge"]

        round_1_results = self.run_round_1(user_prompt, active_agents, callback=round_1_cb)
        round_2_results = self.run_round_2(user_prompt, round_1_results, active_agents, callback=round_2_cb)
        final_result = self.run_round_3(user_prompt, round_1_results, round_2_results, judge)

        return {
            "round_1": round_1_results,
            "round_2": round_2_results,
            "final": final_result
        }