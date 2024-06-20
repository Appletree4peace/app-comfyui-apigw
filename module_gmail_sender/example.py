from gmail_sender import GmailSender

def main():
    # send mail
    sender = GmailSender()
    #sender.send('Test Subject', '<b>This is a test message.</b>')

    # fetch mail with a title regex
    regex_str = 'OzBargain'
    messages = sender.list_messages('admin@cloudelivery.com.au', fr'{regex_str}', 10)
    # print(messages)
    message = sender.get_message('admin@cloudelivery.com.au', messages[0]['id'])
    print(message)


if __name__ == '__main__':
    main()
