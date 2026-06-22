from cop_thief.sdk.sdk import CopThiefSDK


def main():
    sdk = CopThiefSDK()
    results = sdk.run_game()
    print(f"Final scores: {results['final_scores']}")
    print("Transcript saved to results/transcript.jsonl")
    print("Cost report saved to results/cost_report.json")


if __name__ == "__main__":
    main()
