"""Console script for chat_replay_downloader."""
import argparse
import sys
import os
import codecs
import csv
import json
import traceback

from .chat_replay_downloader import *

from .sites.common import ChatDownloader

# from .errors import (
#     LoadError
# )

#from .chat_replay_downloader import char

def main():
    """Console script for chat_replay_downloader."""

    default_init_params = ChatDownloader._DEFAULT_INIT_PARAMS
    default_params = ChatDownloader._DEFAULT_PARAMS

    parser = argparse.ArgumentParser(
        description='A simple tool used to retrieve YouTube/Twitch chat from past broadcasts/VODs. No authentication needed!',
        formatter_class=argparse.RawTextHelpFormatter)

    # PROGRAM PARAMS
    parser.add_argument('url', help='YouTube/Twitch video URL')

    parser.add_argument('--start_time', '-s', default=default_params['start_time'],
                        help='start time in seconds or hh:mm:ss\n(default: %(default)s)')
    parser.add_argument('--end_time', '-e', default=default_params['end_time'],
                        help='end time in seconds or hh:mm:ss\n(default: %(default)s = until the end)')

    parser.add_argument('--message_type', choices=['messages', 'superchat', 'all'], default=default_params['message_type'],
                        help='types of messages to include [YouTube only]\n(default: %(default)s)')

    parser.add_argument('--chat_type', choices=['live', 'top'], default=default_params['chat_type'],
                        help='which chat to get messages from [YouTube only]\n(default: %(default)s)')

    parser.add_argument('--output', '-o', default=default_params['output'],
                        help='name of output file\n(default: %(default)s = print to standard output)')

    parser.add_argument('--logging', '-l', choices=['normal', 'none', 'debug'], default=default_params['logging'],
                        help='level of logging to show\n(default: %(default)s)')

    parser.add_argument('--max_attempts', '-m', default=default_params['max_attempts'],
                        help='maximum number of attempts to make for an http request\n(default: %(default)s)')



    # INIT PARAMS
    parser.add_argument('--cookies', '-c', default=default_init_params['cookies'],
                        help='name of cookies file\n(default: %(default)s)')


    # normal = just print the messages
    # none = completely hide output
    # debug = show a lot more information



    args = parser.parse_args()

    # TODO temp:
    args.logging = 'debug'

    def print_error(message):
        print(message)
        if(args.logging == 'debug'):
            traceback.print_exc()

    options = {}
    init_params = {}

    args_dict = args.__dict__
    for key in args_dict:
        if(key in default_init_params): # is an init param
            init_params[key] = args_dict[key] # set initialisation parameters
        elif(key in default_params): # is a program param
            options[key] = args_dict[key] # set program/get_chat_messages parameters
        else: # neither
            pass


    #     default_init_params = ChatDownloader._DEFAULT_INIT_PARAMS
    # default_params = ChatDownloader._DEFAULT_PARAMS



    #     'cookies' : args.cookies,
    # }



    #
    #  = args.__dict__.copy()
    # {
    #     'url': args.url,
    #     'start_time' : args.start_time,
    #     'end_time': args.end_time,
    #     'message_type': args.message_type,
    #     'chat_type': args.chat_type,
    #     'output': args.output,

    #     'logging': args.logging
    # }


    downloader = ChatReplayDownloader(init_params)


    try:
        q = downloader.get_chat_messages(options) # TODO  returns None?




    except NoChatReplay as e:
        print(e)

    except ParsingError as e:
        print_error('ParsingError occurred')

    except ConnectionError:
        print_error('ConnectionError - unable to connect')
        pass

    except KeyboardInterrupt:
        print('keyboard interrupt')
        #print_error('KeyboardInterrupt')
        pass
    #finally:


    print('got',len(options.get('messages')),'messages')

    message_types = []
    action_types = []

    for message in options.get('messages'):
        message_type = message.get('message_type')
        if(message_type not in message_types):
            message_types.append(message_type)

        action_type = message.get('action_type')
        if(action_type not in action_types):
            action_types.append(action_type)


    print('message_types',message_types)
    print('action_types',action_types)


    with open('test.json', 'w') as outfile:
        json.dump(options.get('messages'), outfile, indent=4, sort_keys=True)
    #print(options.get('messages'))


    #print(json.dumps(options.get('messages'), indent=4))

    #z = a.get('messages')

    #print(q)
    #print('got',len(z),'messages')

    return

    if(args.hide_output):
        f = open(os.devnull, 'w')
        sys.stdout = f
        sys.stderr = f
    else:
        # set encoding of standard output and standard error
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

    try:
        chat_downloader = ChatReplayDownloader(cookies=args.cookies)

        num_of_messages = 0

        def print_item(item):
            chat_downloader.print_item(item)

        def write_to_file(item):

            # only file format capable of appending properly
            with open(args.output, 'a', encoding='utf-8') as f:
                if('ticker_duration' not in item):  # needed for duplicates
                    num_of_messages += 1
                    print_item(item)
                    text = chat_downloader.message_to_string(item)
                    print(text, file=f)

        callback = None if args.output is None else print_item
        if(args.output is not None):
            if(args.output.endswith('.json')):
                pass
            elif(args.output.endswith('.csv')):
                fieldnames = []
            else:
                open(args.output, 'w').close()  # empty the file
                callback = write_to_file

        chat_messages = chat_downloader.get_chat_replay(
            args.url,
            start_time=args.start_time,
            end_time=args.end_time,
            message_type=args.message_type,
            chat_type=args.chat_type,
            callback=callback
        )

        if(args.output is not None):
            if(args.output.endswith('.json')):
                num_of_messages = len(chat_messages)
                with open(args.output, 'w') as f:
                    json.dump(chat_messages, f, sort_keys=True)

            elif(args.output.endswith('.csv')):
                num_of_messages = len(chat_messages)
                fieldnames = []
                for message in chat_messages:
                    fieldnames = list(set(fieldnames + list(message.keys())))
                fieldnames.sort()

                with open(args.output, 'w', newline='', encoding='utf-8') as f:
                    fc = csv.DictWriter(f, fieldnames=fieldnames)
                    fc.writeheader()
                    fc.writerows(chat_messages)

            print('Finished writing', num_of_messages,
                  'messages to', args.output, flush=True)

    except InvalidURL as e:
        print('[Invalid URL]', e)
    except ParsingError as e:
        print('[Parsing Error]', e)
    except NoChatReplay as e:
        print('[No Chat Replay]', e)
    except VideoUnavailable as e:
        print('[Video Unavailable]', e)
    except TwitchError as e:
        print('[Twitch Error]', e)
    except (LoadError, CookieError) as e:
        print('[Cookies Error]', e)
    except KeyboardInterrupt:
        print('Interrupted.')
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
