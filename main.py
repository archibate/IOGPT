import os
import json
import atexit
import subprocess
import traceback

def read_file_content(filename: str) -> str:
    try:
        with open(filename, 'r') as f:
            content = f.read()
            return f'Content of {filename}:\n{content}'
    except FileNotFoundError:
        return f'No such file or directory: {filename}'
    except:
        return traceback.format_exc()

def write_file_content(filename: str, content: str) -> str:
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f'File {filename} written successfully'
    except FileNotFoundError:
        return f'No such file or directory: {filename}'
    except:
        return traceback.format_exc()

def list_files(directory: str) -> str:
    try:
        return f'List of directory {directory}:\n' + '\n'.join(os.listdir(directory))
    except FileNotFoundError:
        return f'No such file or directory: {directory}'
    except:
        return traceback.format_exc()

def google_search(term: str) -> str:
    while True:
        try:
            import googlesearch
            output = ''
            for res in googlesearch.search(term, num_results=7, sleep_interval=0.5, advanced=True):  # type: ignore
                # output += f'=== Google Result {i + 1} ===\n'
                output += '\n'
                output += f'Title: {res.title}\n'
                output += f'URL: {res.url}\n'
                output += f'Brief: {res.description}\n'
            if not output:
                return '(No results found, maybe try a different keyword)'
            output += '\n* For web page you interested, use @BROWSE <url> to read more.'
            return output
        except:
            while True:
                traceback.print_exc()
                retry = input('\n(r)etry (q)uit? ')
                if retry == 'r':
                    break
                if retry == 'q':
                    return traceback.format_exc()

def browse_webpage(url: str) -> str:
    while True:
        try:
            import trafilatura
            print('==> Fetching URL...')
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return f"Fails to get string from url: {url}"
            response = trafilatura.extract(downloaded)
            if not response:
                return f"Fails to parse page: {url}"
            return summerize_text(response)
        except:
            while True:
                traceback.print_exc()
                retry = input('\n(r)etry (q)uit? ')
                if retry == 'r':
                    break
                if retry == 'q':
                    return traceback.format_exc()

def summerize_text(text, thres=200, chunk=500, budget=2000):
    if len(text) < thres:
        return text
    while True:
        try:
            import openai
            import openai_summarize
            print('==> Summerizing...')
            summerizer = openai_summarize.OpenAISummarize(openai.api_key)
            summary = summerizer.summarize_text(text, max_chunk_size=chunk, max_combined_summary_size=budget)
            return summary
        except:
            while True:
                traceback.print_exc()
                retry = input('\n(r)etry (q)uit? ')
                if retry == 'r':
                    break
                if retry == 'q':
                    return text

def execute_shell_command(command: str) -> str:
    with subprocess.Popen(
        args=['bash'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as p:
        try:
            command = 'set -e\n' + command
            input = command.encode()
            output, error = p.communicate(input)
            output = output.decode()
            error = error.decode()
            if error:
                if output:
                    output = output + '\n' + error
                else:
                    output = error
            return output
            # exitcode = p.returncode
            # return f'{output}\n(exited {exitcode})' if not output or exitcode else output
        except:  # Including KeyboardInterrupt, wait handled that.
            p.kill()
            return traceback.format_exc()

def process_command(command: str) -> str:
    command = command.strip()
    if command.startswith("@READ "):
        filename = command[len("@READ "):]
        filename = filename.strip()
        return read_file_content(filename)
    elif command.startswith("@EXIT "):
        exitcode = command[len("@EXIT "):]
        exitcode = int(exitcode)
        raise SystemExit(exitcode)
    elif command.startswith("@WRITE "):
        filename = command[len("@WRITE "):]
        filename = filename.split('[[[', maxsplit=2)
        if len(filename) == 2:
            filename, content = filename
            if content.endswith(']]]'):
                content = content[:-len(']]]')]
        else:
            filename, = filename
            content = ''
        filename = filename.strip()
        content = content.strip()
        return write_file_content(filename, content)
    elif command.startswith("@LIST "):
        directory = command[len("@LIST "):]
        directory = directory.strip()
        return list_files(directory)
    elif command.startswith("@SHELL "):
        cmd = command[len("@SHELL "):]
        cmd = cmd.split('[[[', maxsplit=2)
        if len(cmd) == 2:
            _, cmd = cmd
        else:
            cmd, = cmd
        if cmd.endswith(']]]'):
            cmd = cmd[:-len(']]]')]
        cmd = cmd.strip()
        return execute_shell_command(cmd)
    elif command.startswith("@GOOGLE "):
        keyword = command[len("@GOOGLE "):]
        return google_search(keyword)
    elif command.startswith("@BROWSE "):
        url = command[len("@BROWSE "):]
        return browse_webpage(url)
    elif command[0] == '@' and ' ' in command:
        if command[1:command.index(' ')].isupper():
            return f'Unknown command: {command}'
    return ''

def process_answer(input) -> str:
    multi_line_command = False
    command = ''
    outputs = ''
    for line in input.splitlines():
        line = line.strip()
        if multi_line_command:
            command += line + '\n'
            if line.endswith(']]]'):
                output = process_command(command)
                outputs += output + '\n'
                multi_line_command = False
                command = ''
        else:
            if '@' in line:
                command = line[line.rindex('@'):]
                if command.endswith('[[['):
                    multi_line_command = True
                    command += '\n'
                else:
                    output = process_command(command)
                    outputs += output + '\n'
                    command = ''
    return outputs

def compose_hint(result: str, question: str, curfile: str, rounds: int) -> str:
    content = ''
    if result:
        query = result + '\n' + question
    else:
        query = question
    if not query.strip():
        print('==> Got empty message, exiting')
        raise SystemExit(0)
    if not result and curfile:
        content += f'\n* Current file: {curfile}'
        # listdir = os.listdir('.')
        # if len(listdir) < 8:
        #     listdir = ' '.join(listdir)
        #     content += f'\n* Current directory contains: {listdir}'
    if rounds > 0:
        content = query + content
        content += f'\n* Keep using the @ format to solve problems step by step, no nature languages.'
    else:
        content += r'''
* You must answer using @ commands, available commands are:
1. Read file: @READ <path>
2. Write file: @WRITE <path> [[[
<content>
]]]
3. Append to file: @APPEND <path> [[[
<content>
]]]
4. Shell command: @SHELL [[[
<command>
]]]
5. List directory: @LIST <dir>
6. Google search: @GOOGLE <term>
Do not invent new commands not in this list.'''
        content += r'''
* To solve the problem, you may need to read file content to complete the answer, so feel free to ask me which file you want to read. You don't have to complete the answer in one round, you may first ask some details about my file, for example, asking me to provide the file content. To ask me to provide file content, you need to answer in this format: @READ hello.cpp. After you got enough details to complete the answer, you may write to files. To create or overwrite an file named hello.cpp with <content>, you need to answer in this format: @WRITE hello.cpp [[[
<content>
]]] You should only answer in @ format, without any additional text, no nature languages.'''
        content = content + '\nNow my question is: ' + query
    return content.strip()

def createbot(model='gpt-3.5-turbo'):
    messages = []
    @atexit.register
    def _():
        with open('messages.json', 'w') as f:
            json.dump(messages, f)
    def ask(question):
        # print('-=-=-=- QUESTION -=-=-=-')
        # print(question)
        messages.append({'role': 'user', 'content': question})
        while True:
            print('==> Thinking...')
            try:
                import openai
                completion = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=1,
                    top_p=1,
                    n=1,
                    presence_penalty=0,
                    frequency_penalty=0,
                    stream=False)
            except:
                print('-=-=-=- AI ERROR -=-=-=-')
                traceback.print_exc()
                completion = None
            if not completion:
                while True:
                    retry = input('\n(r)etry (q)uit? ')
                    if retry == 'r':
                        break
                    if retry == 'q':
                        raise SystemExit(-1)
                continue
            choices = completion.choices  # type: ignore
            response = choices[0].message.content
            print('-=-=-=- AI RESPONSE -=-=-=-')
            print(response)
            messages.append({'role': 'assistant', 'content': response})
            while True:
                accept = input('\n(a)ccept (r)eset (p)rompt (q)uit? ')
                if accept == 'a' or not accept:
                    return response
                if accept == 'p' or not accept:
                    prompt = input('> ')
                    messages.append({'role': 'user', 'content': prompt})
                    continue
                if accept == 'r':
                    messages.pop()
                    print('==> REGENERATING')
                    break
                if accept == 'q':
                    raise SystemExit(0)
    return ask

def main():
    bot = createbot()
    curfile = ''
    rounds = 0
    result = ''
    while True:
        try:
            line = input('> ')
        except EOFError:
            break
        question = line.rstrip()
        hint = compose_hint(result, question, curfile, rounds)
        answer = bot(hint)
        result = process_answer(answer)
        print('-=-=-=- CMD RESULT -=-=-=-')
        print(result)
        rounds += 1

if __name__ == '__main__':
    # print(process_answer('For using the @READ command, I can type @READ hello.cpp'))
    # print(process_answer('@LIST .'))
    # print(process_answer('@READ hello.cpp'))
    # print(process_answer('@SHELL [[[\nls\n]]]'))
    main()
