import openai

system = r'''For each Q, give A answering the question "Does this look like a valid and complete web page?" Examples:
Q: JavaScript is required to run this page. Please upgrade your browser.
A: No.
Q: (place vulkan-introduction.md.html here)
A: No.
Q: As we all know, Chess and Chinese Chess (XiangQi) are two board games that share similar structure and goal: to capture the opposing King.
A: Yes.
Q: 1. Introducting the Background What are memory allocators, and why are they useful?
A: Yes.
Q: Not Found
A: No.
Q: 404 Not found - GitHub
A: No.
Q: In this tutorial, you will learn all fundemental skills on how to draw a simple triangle in ~1000 lines of C-styled C++ using the neo-frontier technology named Vulkan.
A: Yes.
Q: Reading time: 21 mins. Ray-tracing is one of the most elegant techniques in computer graphics. Many phenomena that are difficult or impossible with other techniques are simple with ray tracing, including shadows, reflections, and refracted light". Robert L. Cook Thomas Porter Loren Carpenter. "Distributed Ray-Tracing" (1984).
A: Yes.
Q: 404 Error - The page is not found, but you may support UNICEF to find missing children.
A: No.
Q: Zhihu - You seems to entered a region with no knowledge.
A: No.
Q: GitDailies Get a daily snapshot of Commit and PR activity. Engineers and managers can quickly see today's changes, but avoid distracting notifications.
A: Yes.
Q: This is not the web page you are looking for. Find code, projects, and people on GitHub: Search or jump to... Contact Support — GitHub Status — @githubstatus
A: No.
Q: Oops, we ran into a trouble, the content is missing.
A: No.
Q: CMake latest release (3.26.3) FindGTest Locate the Google C++ Testing Framework. New in version 3.20: Upstream GTestConfig.cmake is used if possible.
A: Yes.
Q: {}
A:
'''

if __name__ == '__main__':
    query = '''List models
GET https://api.openai.com/v1/models
Lists the currently available models, and provides basic information about each one such as the owner and availability.'''

    prompt = system.format(query.replace('\n', ' ').strip())
    print(prompt)
    completion = openai.Completion(engine='davinci', prompt=prompt, max_tokens=20, temperature=0.1)
    print(completion)
