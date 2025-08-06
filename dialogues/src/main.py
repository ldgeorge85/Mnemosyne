"""
Entry point for the Philosophical Multi-Agent Debate System.
"""

from agents.orchestrator import OrchestratorAgent

def main():
    """Main function to start the debate system."""
    orchestrator = OrchestratorAgent()
    print("\nWelcome to the Philosophical Multi-Agent Debate System!")
    print("Press Enter without typing anything to use a sample prompt.\n")
    prompt = input("Enter a philosophical prompt: ")
    if not prompt.strip():
        prompt = "Is it better to seek happiness or to seek meaning in life?"
        print(f"Using sample prompt: {prompt}\n")
    orchestrator.run(prompt)

if __name__ == "__main__":
    main()

