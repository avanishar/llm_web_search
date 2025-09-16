from get_links import get_links
from scrape import scrape_links, initialize_logs
from cleaning import combine_logs
from llm import call_gemini, context_combine_prompt

topic = "latest ai news for today"

links = get_links(topic)
log_folder = initialize_logs(topic)

results = scrape_links(links, save_logs=True, log_folder=log_folder)

print("\n\033[92m✅ Successful scrapes:\033[0m", len(results["success"]))
print("\033[91m❌ Failed scrapes:\033[0m", len(results["errors"]))

if len(results["success"]) == 0:
    print("\033[91mNo successful scrapes. Exiting.\033[0m")
    exit()

context_from_logs = combine_logs(log_folder)

final_prompt = context_combine_prompt(context_from_logs, topic)

print("\033[96m🤖 Sending to LLM...\033[0m")
answer = call_gemini(final_prompt)

print("\n\033[92m💡 Final Answer:\033[0m\n")
print(answer)
