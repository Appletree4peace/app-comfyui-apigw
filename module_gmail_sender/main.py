# Example code to use the module:

from gmail_sender import GmailSender

def main():
    sender = GmailSender()
    sender.send('Test subject', '<b>Your HTML Message Content Here</b>')

if __name__ == '__main__':
    main()
