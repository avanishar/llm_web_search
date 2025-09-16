from get_links import get_links
from scrape import scrape_links, initialize_logs
from cleaning import combine_logs
from llm import call_gemini, context_combine_prompt

def main():
    topic = input("\033[96m🔍 Enter your topic:\033[0m ").strip()
    if not topic:
        print("\033[91m❌ No topic entered. Exiting.\033[0m")
        return

    # Get search links
    links = get_links(topic)
    if not links:
        print("\033[91m❌ No links found for your topic.\033[0m")
        return

    print("\033[96m🔗 Found links:\033[0m")
    for link in links:
        print("   ", link)

    # Initialize logs
    log_folder = initialize_logs(topic)

    # Scrape
    results = scrape_links(links, save_logs=True, log_folder=log_folder)

    print("\n\033[92m✅ Successful scrapes:\033[0m", len(results["success"]))
    print("\033[91m❌ Failed scrapes:\033[0m", len(results["errors"]))

    if len(results["success"]) == 0:
        print("\033[91m❌ No successful scrapes. Exiting.\033[0m")
        return

    # Combine scraped logs
    context_from_logs = combine_logs(log_folder)

    # Prepare final prompt
    final_prompt = context_combine_prompt(context_from_logs, topic)

    # Get LLM answer
    print("\n\033[96m🤖 Sending to Gemini...\033[0m")
    answer = call_gemini(final_prompt)

    print("\n\033[92m💡 Final Answer:\033[0m\n")
    print(answer)

if __name__ == "__main__":
    main()
